from django.core.management.base import BaseCommand
from django.db import transaction
from quotes.models import Author, Quote, Tag
import pymongo

class Command(BaseCommand):
    help = 'Migrate quotes and authors from MongoDB to Django (Postgres)'

    def add_arguments(self, parser):
        parser.add_argument('--mongo-uri', default='mongodb://localhost:27017/', help='MongoDB URI')
        parser.add_argument('--db', default='quotesdb', help='Mongo DB name')
        parser.add_argument('--quotes-coll', default='quotes', help='Quotes collection name')
        parser.add_argument('--authors-coll', default='authors', help='Authors collection name')

    def handle(self, *args, **options):
        client = pymongo.MongoClient(options['mongo_uri'])
        db = client[options['db']]
        quotes_coll = db[options['quotes_coll']]
        authors_coll = db[options['authors_coll']]

        with transaction.atomic():
            # migrate authors
            for a in authors_coll.find():
                name = a.get('name') or a.get('fullname')
                if not name:
                    continue
                Author.objects.update_or_create(
                    name=name,
                    defaults={
                        'born_date': a.get('born_date') or '',
                        'born_location': a.get('born_location') or '',
                        'description': a.get('description') or ''
                    }
                )

            # migrate quotes
            for q in quotes_coll.find():
                text = q.get('text') or q.get('quote') or ''
                author_name = q.get('author') or (q.get('author_name') if isinstance(q.get('author_name'), str) else None)
                if not text or not author_name:
                    continue
                author_obj, _ = Author.objects.get_or_create(name=author_name)
                quote_obj, created = Quote.objects.get_or_create(text=text, author=author_obj)
                tags = q.get('tags') or []
                for tn in tags:
                    tag_obj, _ = Tag.objects.get_or_create(name=tn)
                    quote_obj.tags.add(tag_obj)

        self.stdout.write(self.style.SUCCESS('Migration from MongoDB finished.'))
