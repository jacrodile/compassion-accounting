
def migrate(cr, version):
    if version:
        cr.execute(
            "update recurring_contract_group "
            "set invoice_day = COALESCE(CAST(EXTRACT(day FROM recurring_contract.next_invoice_date) as varchar), '1')"
            "from recurring_contract_group c "
            "inner join recurring_contract on group_id = c.id"
        )
        cr.execute("""
        update recurring_contract_group
        set invoice_suspended_until = (
            select date_trunc('month', min(next_invoice_date)) from recurring_contract
            where group_id = recurring_contract_group.id
            and state in ('waiting','active')
            and child_id is not null
            and next_invoice_date > (
                CURRENT_DATE + INTERVAL '1 month' * recurring_contract_group.advance_billing_months + INTERVAL '1 month'
            )
            group by group_id
            having count(*) = 1)
        """)
