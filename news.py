
import random

NEWS_TEMPLATES = {
    "crypto": [
        ("Positive", "New institutional investment in {asset}! Prices are soaring."),
        ("Positive", "{asset} breaks resistance level, analysts predict further gains."),
        ("Negative", "Regulatory concerns loom over {asset}, causing a price drop."),
        ("Negative", "Major exchange hack leads to widespread {asset} sell-off."),
    ],
    "stocks": [
        ("Positive", "{asset} reports record earnings, stock jumps."),
        ("Positive", "New product announcement from {asset} excites investors."),
        ("Negative", "{asset} misses earnings estimates, stock tumbles."),
        ("Negative", "Supply chain issues plague {asset}, leading to lower forecast."),
    ],
    "forex": [
        ("Positive", "Strong economic data boosts {pair} value."),
        ("Negative", "Political instability weakens {pair}."),
    ],
    "generic": [
        ("Positive", "Overall market sentiment is bullish."),
        ("Negative", "Fear of recession leads to market-wide sell-off."),
    ],
    "indices": [
        ("Positive", "Strong jobs report sends indices soaring."),
        ("Negative", "Inflation fears cause a broad market downturn."),
    ],
    "bonds": [
        ("Positive", "Fed hints at rate cuts, bond yields fall."),
        ("Negative", "Unexpectedly high inflation data sends bond yields higher."),
    ]
}

current_event = None

def get_market_news(asset_type, asset_id):
    global current_event
    # Let events persist for a bit
    if current_event and random.random() < 0.995:
        return current_event

    # 0.2% chance of a new event
    if random.random() < 0.002:
        category = random.choices([asset_type, "generic"], weights=[0.7, 0.3], k=1)[0]
        
        if category == "forex":
            template_asset_id = asset_id
        else:
            template_asset_id = asset_id.split('/')[0] # For pairs like 'EUR/USD'

        sentiment, template = random.choice(NEWS_TEMPLATES[category])
        headline = template.format(asset=template_asset_id, pair=template_asset_id)
        
        # Determine effect
        magnitude = random.uniform(0.01, 0.05) # 1% to 5% drift
        if sentiment == "Negative":
            magnitude *= -1

        current_event = {
            "headline": headline,
            "sentiment": sentiment,
            "magnitude": magnitude,
            "target_asset": asset_id if category != "generic" else "all"
        }
        return current_event
    
    # ~99.8% chance of no news
    current_event = None
    return None
