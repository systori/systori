from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from optparse import make_option
from systori.apps.task.models import *
from systori.apps.document.models import *

DOC_TYPES = {
    'invoice': Invoice,
    'proposal': Proposal
}
class Command(BaseCommand):
    args = "[%s] <doc_id ...>" % '|'.join(DOC_TYPES.keys())
    help = "Triggers the re-generation of documents and updates paths to the new files."
    option_list = BaseCommand.option_list + (
        make_option("-l", "--language",
            action='store', type='string', dest='lang',
            default='en-us', help='Specify language for document.'),
    )

    def handle(self, *args, **options):

        translation.activate(options['lang'])

        if not args:
            raise CommandError('Must specify document type and document id. Use --help for more.')

        doctype_name = args[0]
        if doctype_name not in DOC_TYPES.keys():
            raise CommandError('Document type "%s" not supported, try one of: %s' % (doctype_name, ', '.join(DOC_TYPES.keys())))

        doctype = DOC_TYPES[doctype_name]

        for doc_id in args[1:]:

            try:
                document = doctype.objects.get(pk=int(doc_id))
            except doctype.DoesNotExist:
                raise CommandError(doctype_name+' with id "%s" does not exist.' % doc_id)

            document.generate_document()

            self.stdout.write('- %s %s -' % (doctype_name, doc_id))
            self.stdout.write('generated: %s' % document.email_pdf.path)
            self.stdout.write('generated: %s' % document.print_pdf.path)