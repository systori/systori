from rest_framework.routers import DefaultRouter

from systori.apps.document.api import (
    DocumentTemplateModelViewSet,
    TimesheetModelViewSet,
    ProposalModelViewSet,
    PaymentModelViewSet,
    InvoiceModelViewSet,
    AdjustmentModelViewSet,
    RefundModelViewSet,
)

router = DefaultRouter()
router.register(r"documenttemplate", DocumentTemplateModelViewSet)
router.register(r"timesheet", TimesheetModelViewSet)
router.register(r"proposal", ProposalModelViewSet)
router.register(r"payment", PaymentModelViewSet)
router.register(r"invoice", InvoiceModelViewSet)
router.register(r"adjustment", AdjustmentModelViewSet)
router.register(r"refund", RefundModelViewSet)


urlpatterns = router.urls
