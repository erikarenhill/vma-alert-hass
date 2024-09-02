"""Services for VMA Alert integration."""
from __future__ import annotations

import random
from datetime import datetime
import uuid

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

CITIES = [
    "Stockholm", "Göteborg", "Malmö", "Uppsala", "Västerås", "Örebro", "Linköping", "Helsingborg",
    "Jönköping", "Norrköping", "Lund", "Umeå", "Gävle", "Borås", "Eskilstuna", "Södertälje",
    "Karlstad", "Täby", "Växjö", "Halmstad"
]

MESSAGES = [
    "Det brinner i {city}, stäng dörrar och fönster.",
    "Gasutsläpp i {city}, gå inomhus och stäng ventilationen.",
    "Översvämning i {city}, undvik lågt liggande områden.",
    "Kemikalieolycka i {city}, håll er inomhus och följ myndigheternas råd.",
    "Kraftigt oväder närmar sig {city}, säkra lösa föremål utomhus."
]

def setup_services(hass: HomeAssistant) -> None:
    """Set up services for VMA Alert integration."""

    async def simulate_vma_event(call: ServiceCall) -> None:
        """Simulate a VMA event."""
        city = random.choice(CITIES)
        message = random.choice(MESSAGES).format(city=city)
        timestamp = datetime.now().isoformat()
        identifier = f"TEST-VMA-{uuid.uuid4().hex[:8].upper()}"

        simulated_data = {
            "identifier": identifier,
            "sent": timestamp,
            "status": "Test",
            "msgType": "Alert",
            "info": [{
                "language": "sv-SE",
                "category": "Safety",
                "event": "Viktigt meddelande till allmänheten (VMA)",
                "urgency": "Immediate",
                "severity": "Severe",
                "certainty": "Observed",
                "description": message,
                "area": [{"areaDesc": city}]
            }]
        }

        hass.bus.fire("vma_alert_event", simulated_data)

    hass.services.async_register(DOMAIN, "simulate_vma_event", simulate_vma_event)