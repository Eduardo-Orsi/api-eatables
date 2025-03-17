import os

import requests

from ..integration.yampi import Yampi
from ..integration.bling import Bling
from ..integration.shopify import ShopifyIntegration
from ..db.database import not_async_get_db


YAMPI_TOKEN = os.getenv("YAMPI_TOKEN")
YAMPI_SECRET_KEY = os.getenv("YAMPI_SECRET_KEY")
YAMPI_ALIAS = os.getenv("YAMPI_ALIAS")


def ping_videofy() -> None:
    response = requests.get("https://web.videofy.app/", timeout=10)
    if response.status_code == 200:
        pass
    else:
        print("Videofy is down")

def sync_orders() -> None:
    db = not_async_get_db()
    db.rollback()
    bling = Bling(db_session=db)
    yampi = Yampi(YAMPI_ALIAS, YAMPI_TOKEN, YAMPI_SECRET_KEY)
    shopify = ShopifyIntegration("https://de9306.myshopify.com/", "2024-01")

    bling_orders = bling.get_orders(number_of_orders=100)

    for bling_order in bling_orders["data"]:

        if not bling.is_order_synced(bling_order_id=bling_order["id"]):

            shopify_order_name = yampi.get_shopify_order_name(bling_order["numeroLoja"])
            shopify_order_id = shopify.get_order_id_by_name(shopify_order_name)
            full_bling_order = bling.get_order(bling_order["id"])

            try:
                package = full_bling_order["data"]["transporte"]["volumes"][0]
            except:
                print(f"Order Does Not Need Tracking: {bling_order["numero"]} - {bling_order["contato"]["nome"]}")
                continue
            tracking_method = get_tracking_method(package)

            shopify.add_tracking_code(
                order_id=shopify_order_id,
                tracking_company=tracking_method["tracking_company"],
                tracking_number=tracking_method["tracking_number"],
                tracking_url=tracking_method["tracking_url"]
            )

            print(f"Tracking Code Added to Shopify: {shopify_order_id}")

            bling.mark_order_as_synced(
                bling_order_id=bling_order["id"],
                yampi_id=bling_order["numeroLoja"],
                shopify_order_id=shopify_order_id,
                tracking_code=tracking_method["tracking_number"],
                tracking_campany=tracking_method["tracking_company"],
                tracking_url=tracking_method["tracking_url"]
            )

            print(f"Order Marked as Synced: {bling_order["numero"]} - {bling_order["contato"]["nome"]}")
        else:
            print(f"Order Alredy Synced: {bling_order["numero"]} - {bling_order["contato"]["nome"]}")
    db.close()


def get_tracking_method(package: dict) -> dict:
    if package.get("servico") == "Expresso":
        return {
            "tracking_company": "Total Express",
            "tracking_number": package.get("codigoRastreamento"),
            "tracking_url": f"https://totalconecta.totalexpress.com.br/rastreamento/?codigo={package.get("codigoRastreamento")}"
        }
    elif package.get("servico") == "Econômico (Coleta recorrente)":
        return {
            "tracking_company": "Loggi",
            "tracking_number": package.get("codigoRastreamento"),
            "tracking_url": "https://www.loggi.com/rastreador/"
        }
    elif package.get("servico") in ["PAC CONTRATO AG", "SEDEX CONTRATO AG"]:
        return {
            "tracking_company": "Correios",
            "tracking_number": package.get("codigoRastreamento"),
            "tracking_url": "https://rastreamento.correios.com.br/app/index.php"
        }
    else:
        return {
            "tracking_company": "Transportadora",
            "tracking_number": package.get("codigoRastreamento"),
            "tracking_url": "https://lovechocolate.com.br/pages/rastreio"
        }
