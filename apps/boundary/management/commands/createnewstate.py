from django.db.models import Max
from django.core.management.base import BaseCommand
from common.models import Language
from boundary.models import Boundary, BoundaryStateCode


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('statename')
        parser.add_argument('statecode')
        parser.add_argument('lang')

    def createstate(self, statename, statecode, langcode):
        try:
            Boundary.objects.get(name=statename, boundary_type_id='ST')
            print("State: "+statename+" already exists")
            return False
        except:
            print("Creating new state")

        maxstateid = Boundary.objects.filter(boundary_type_id='ST').aggregate(
                                                              max_id=Max('id'))
        newstateid = maxstateid['max_id']+1
        state_id = Boundary.objects.create(id=newstateid,
                                           name=statename,
                                           dise_slug=statename,
                                           boundary_type_id='ST',
                                           parent_id=1,
                                           status_id='AC')

        BoundaryStateCode.objects.create(char_id=statecode, boundary=state_id,
                                         language=langcode)
        return True

    def handle(self, *args, **options):
        statename = options.get('statename', None).title()
        if not statename:
            print("Please specify a statename argument")
            return False

        statecode = options.get('statecode', None).lower()
        if not statecode:
            print("Please specify a statecode argument")
            return False

        lang = options.get('lang', None)
        if not lang:
            print("Please specify a language argument")
            return False
        try:
            # lang_code = Language.objects.get(name=lang.title())
            lang_code = Language.objects.get(char_id=lang)  # changed by 4Edge
        except Exception as e:
            print(e)
            print("Enter a valid lanaguage")
            return False

        if self.createstate(statename, statecode, lang_code):
            print("New state created: "+statename)
