import logging

from dateutil.utils import today
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # Retrieve balance product
    balance_product = env["product.product"].search([("name", "=", "Balance")])
    if len(balance_product.ids) != 1:
        _logger.warning("balance product is not unique")
        return 1
    # retrieve all contract line
    contract_lines = env["recurring.contract"].search([("state", "not in", ["cancelled", "terminated"])]).mapped(
        "contract_line_ids")
    for contract_line in contract_lines:
        # Calculated the correct price of a line
        expected_price = contract_line.contract_id.pricelist_id.get_product_price(contract_line.product_id,
                                                                                  contract_line.quantity,
                                                                                  contract_line.contract_id.partner_id,
                                                                                  today())
        # if there's a difference we balance it in a new line
        if contract_line.amount != expected_price and contract_line.product_id.pricelist_item_count > 0:
            balance_price = contract_line.amount - expected_price
            # Try to find an existing balance line of a contract
            balance_line = contract_line.contract_id.contract_line_ids.filtered(
                lambda l: l.product_id == balance_product)
            # we had the balance amount if a balance line exist or we create the balance line
            if balance_line:
                _logger.info(
                    f"Balance contract line found old amount: {balance_line.amount}, for contract {contract_line.contract_id}")
                balance_line.write({"amount": balance_line.amount + balance_price})
                _logger.info(
                    f"Balance contract line populated new amount: {balance_line.amount}, for contract {contract_line.contract_id}")
            else:
                balance_line = env["recurring.contract.line"].create({
                    "amount": balance_price,
                    "product_id": balance_product.id,
                    "quantity": 1,
                    "contract_id": contract_line.contract_id.id
                })
                _logger.info(f"Balance contract line created {balance_line} for contract {contract_line.contract_id}")
            contract_line.write({"amount": expected_price})
    _logger.info("Migration done!")
