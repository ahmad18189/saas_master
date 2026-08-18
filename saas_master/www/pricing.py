from saas_master.marketing_i18n import apply_marketing_context


def get_context(context):
	apply_marketing_context(context, page="pricing")
	return context
