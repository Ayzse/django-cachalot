from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps
from ...api import invalidate


class Command(BaseCommand):
    help = 'Invalidates the cache keys set by django-cachalot.'
    args = '[app_label[.modelname] [...]]'
    option_list = BaseCommand.option_list + (
        make_option('-c', '--cache', action='store', dest='cache_alias',
                    type='choice', choices=list(settings.CACHES.keys()),
                    help='Cache alias from the CACHES setting.'),
        make_option('-d', '--db', action='store', dest='db_alias',
                    type='choice', choices=list(settings.DATABASES.keys()),
                    help='Database alias from the DATABASES setting.'),
    )

    def handle(self, *args, **options):
        cache_alias = options['cache_alias']
        db_alias = options['db_alias']
        verbosity = int(options['verbosity'])

        models = []
        for arg in args:
            try:
                models.extend(apps.get_app_config(arg).get_models())
            except LookupError:
                app_label = '.'.join(arg.split('.')[:-1])
                model_name = arg.split('.')[-1]
                models.append(apps.get_model(app_label, model_name))

        cache_str = '' if cache_alias is None else "on cache '%s'" % cache_alias
        db_str = '' if db_alias is None else "for database '%s'" % db_alias
        keys_str = 'keys for %s models' % len(models) if args else 'all keys'

        if verbosity > 0:
            self.stdout.write(' '.join(filter(bool, ['Invalidating', keys_str,
                                                     cache_str, db_str]))
                              + '...')

        invalidate(*models, cache_alias=cache_alias, db_alias=db_alias)
        if verbosity > 0:
            self.stdout.write('Cache keys successfully invalidated.')
