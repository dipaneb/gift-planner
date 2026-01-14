from enum import StrEnum
from sqlalchemy.dialects.postgresql import ENUM

# enum for python (used for autocomplete in IDE, error detection, etc.)
class GiftStatusEnum(StrEnum):
    idee = "idee"
    achete = "achete"
    commande = "commande"
    en_cours_livraison = "en_cours_livraison"
    livre = "livre"
    recupere = "recupere"
    emballe = "emballe"
    offert = "offert"

# enum for SQL
GiftStatus = ENUM(
    GiftStatusEnum, # passing GiftStatusEnum ensure the two enums are always synchronized 
    name="gift_status",
)
