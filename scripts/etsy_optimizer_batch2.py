"""Fix the 3 failed listings (tags over 20 chars) + optimize remaining 32 listings"""
import json, requests, time, sys

with open('etsy_token.json', 'r') as f:
    token_info = json.load(f)

ACCESS_TOKEN = token_info['access_token']
API_KEY = 'gqnem32usqjmqjaeg0adl0ly'
SHARED_SECRET = 'zrgxhvnrra'
SHOP_ID = '39610840'

HEADERS = {
    'x-api-key': f'{API_KEY}:{SHARED_SECRET}',
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}

OPTIMIZED = [
    # FIX #14 - Cowboy Skeleton (had "cowboy skeleton hoodie" = 22 chars)
    {
        "id": 1845756302,
        "title": "Cowboy Skeleton Metal Hoodie | Southern Rock Gothic Pullover | 90s Groove Metal Sweatshirt | Western Dark Art | Metalhead Gift",
        "description": "Ride into the darkness, partner — this cowboy skeleton hoodie is where southern grit meets gothic metal.\n\nFeaturing a cowboy-hatted skeleton in full western regalia, this hoodie channels the dusty, whiskey-soaked energy of 90s groove metal and southern rock. It's a tribute to the riffs that rattled arenas and the attitude that refused to die.\n\n✦ THE ART\n• Cowboy skeleton graphic — southern gothic at its finest\n• Rich detail with dark western and metal influences\n• A design that tells a story before you say a word\n\n✦ CONSTRUCTION\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket for warmth and convenience\n• Double-lined hood with color-matched drawcord\n• Built tough enough for the road, soft enough for the couch\n\n✦ WHO NEEDS THIS\n→ Fans of groove metal, southern rock, and dark western art\n→ Country-metal crossover enthusiasts\n→ Anyone who wants their hoodie to have as much attitude as they do\n\n🖤 Deathlipse — from the pit to the prairie.",
        "tags": ["cowboy skeleton", "southern rock hood", "groove metal merch", "gothic western art", "90s metal hoodie", "dark cowboy hood", "whiskey culture", "metalhead gift", "skeleton hoodie", "gothic pullover", "country metal", "heavy metal wear", "alt hoodie"]
    },
    # FIX #17 - Type O Negative Pillow (had "type o negative pillow" = 22 chars)
    {
        "id": 1861647439,
        "title": "Type O Negative Pillow | Gothic Metal Home Decor | Dark Art Throw Cushion | Metalhead Bedroom Gift | Goth Room Accent",
        "description": "Bring gothic doom into your living space with this Type O Negative-inspired throw pillow — because even your decor should be heavy.\n\nThis isn't just a pillow — it's a portal to the world of gothic metal, right there on your couch. The design channels the dark, romantic energy of Type O's iconic aesthetic, making it the perfect accent piece for any metalhead's sanctuary.\n\n✦ DESIGN\n• Type O Negative-inspired gothic artwork\n• Rich, moody color palette\n• High-resolution print on premium fabric\n\n✦ PILLOW DETAILS\n• Spun polyester cover — soft and durable\n• Hidden zipper for easy cover removal\n• Machine washable for easy care\n• Available in standard throw pillow size\n\n✦ STYLE YOUR DARK SPACE\n→ Bedroom accent for goth and metal aesthetics\n→ Living room conversation piece\n→ Dorm room upgrade for the alternative student\n→ Gift for the metalhead who's decorated everything else\n\n🖤 Deathlipse — dark art, from head to home.",
        "tags": ["type o pillow", "gothic home decor", "metal throw pillow", "dark art cushion", "goth room decor", "metalhead gift", "band merch home", "doom metal decor", "y2k goth pillow", "alt decor", "dark bedroom", "music fan gift", "gothic accent"]
    },
    # FIX #19 - Suicide Silence (had "suicide silence hoodie" = 22 chars)
    {
        "id": 1846782730,
        "title": "Suicide Silence Inspired Hoodie | Deathcore Band Sweatshirt | Extreme Metal Pullover | Heavy Metal Gift | Dark Art Hoodie",
        "description": "Descend into the abyss with this Suicide Silence-inspired hoodie — deathcore darkness, wearable form.\n\nCapturing the suffocating heaviness and raw brutality of one of deathcore's founding acts, this hoodie is built for those who live in the breakdown. The bold graphic channels the band's relentless energy, making it a staple for extreme metal warriors.\n\n✦ THE DESIGN\n• Brutal deathcore-inspired illustration\n• Bold, high-impact graphic print\n• Captures the intensity of extreme metal\n\n✦ HOODIE SPECS\n• 50% cotton / 50% polyester heavy blend\n• Spacious kangaroo pocket\n• Adjustable drawstring hood\n• Durable construction for pit-tested wear\n• Ethically manufactured\n\n✦ FOR THE\n→ Deathcore faithful and extreme metal warriors\n→ Concert-goers who need pit-ready attire\n→ Anyone who believes there's no such thing as too heavy\n\n🖤 Deathlipse — the sound of darkness, the look of fury.",
        "tags": ["deathcore hoodie", "extreme metal hood", "heavy metal band", "brutal metal hood", "dark art pullover", "metalhead gift", "concert hoodie", "death metal merch", "underground metal", "band sweatshirt", "gothic hoodie", "alt fashion", "metal merch"]
    },

    # === REMAINING 32 LISTINGS (not yet optimized) ===

    # Opeth Mug (Coffee Mug variant)
    {
        "id": 1862046221,
        "title": "Opeth Metal Coffee Mug | Gothic Dark Art Cup | Progressive Rock Gift | Metalhead Home Decor | Black Ceramic Mug",
        "description": "Fuel your mornings with darkness — this Opeth-inspired mug is the perfect vessel for every metalhead's daily ritual.\n\nWhether it's black coffee at dawn or herbal tea at midnight, this ceramic mug channels the haunting beauty of progressive metal into your kitchen. The bold artwork wraps around the mug, turning your daily caffeine hit into an art experience.\n\n✦ SPECS\n• Premium ceramic construction\n• Glossy finish with vivid color reproduction\n• Microwave and dishwasher safe\n• Comfortable C-handle grip\n• 11oz standard capacity\n\n✦ GREAT GIFT FOR\n→ Metal fans who take their coffee black\n→ Gothic home decor collectors\n→ Anyone who needs more darkness in their kitchen\n\n🖤 Deathlipse — dark art for every corner of your life.",
        "tags": ["opeth coffee mug", "metal band mug", "gothic dark art", "prog rock gift", "metalhead decor", "black ceramic mug", "music lover cup", "heavy metal gift", "goth kitchen", "dark art mug", "band merch home", "coffee lover gift", "alt home decor"]
    },
    # Opeth Tank Top (another variant)
    {
        "id": 1861949177,
        "title": "Opeth Tank Top Women | Gothic Metal Racerback | Dark Forest Art | Progressive Band Merch | Festival Concert Top",
        "description": "Embrace the darkness in breathable comfort — this Opeth-inspired tank is made for hot venues and summer festivals.\n\nDesigned with the haunting forest imagery that defines Opeth's visual language, this racerback tank combines gothic art with a flattering feminine cut. Light enough for the pit, beautiful enough for the street.\n\n✦ FIT & FABRIC\n• Soft, luxurious fabric with feminine cut\n• Breathable and lightweight\n• Chunky spaghetti straps\n• Available in multiple sizes\n\n✦ STYLE IT\n→ Solo at summer festivals\n→ Under a leather jacket for layered edge\n→ Paired with high-waist jeans and combat boots\n\n🖤 Deathlipse — dark art, worn beautifully.",
        "tags": ["opeth tank top", "gothic racerback", "metal women tank", "dark forest art", "prog band merch", "festival top", "concert tank", "metalhead gift her", "goth summer top", "alt clothing", "rock music tank", "dark art tank", "band tee women"]
    },
    # Iron Maiden Hoodie
    {
        "id": 1860979861,
        "title": "Iron Maiden Inspired Hoodie | NWOBHM Metal Band Pullover | British Heavy Metal Sweatshirt | Eddie Art Gift | Rock Merch",
        "description": "Up the Irons! This Iron Maiden-inspired hoodie channels four decades of British heavy metal glory.\n\nFrom the East End to every arena on Earth, Iron Maiden's imagery is as iconic as their galloping basslines. This hoodie captures that legendary spirit with bold artwork that any fan will instantly recognize. Built for comfort, designed for the faithful.\n\n✦ THE ARTWORK\n• Iconic British metal-inspired illustration\n• Bold, vivid print that commands respect\n• A tribute to the New Wave of British Heavy Metal\n\n✦ HOODIE QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket and adjustable drawstring\n• One-piece body — no side seams\n• Ethically sourced, OEKO-TEX certified\n\n✦ FOR FANS WHO\n→ Know every word to every album\n→ Need pit-ready comfort\n→ Want to gift a fellow metalhead something epic\n\n🖤 Deathlipse — up the irons, down with the ordinary.",
        "tags": ["iron maiden hoodie", "NWOBHM merch", "british metal band", "heavy metal hoodie", "eddie art hoodie", "rock band pullover", "metalhead gift", "concert hoodie", "80s metal merch", "metal sweatshirt", "alt fashion", "gothic hoodie", "classic metal"]
    },
    # Metallica-style Hoodie
    {
        "id": 1845881024,
        "title": "Thrash Metal Lightning Hoodie | 80s Metal Band Pullover | Skull Electric Art | Heavy Metal Gift | Gothic Rock Sweatshirt",
        "description": "Ride the lightning in this electrifying thrash metal hoodie — where 80s fury meets modern comfort.\n\nInspired by the golden era of thrash, this hoodie features bold lightning-and-skull artwork that channels the raw energy of the genre's founding fathers. Whether you're at a show or just turning heads on the street, this is your daily armor.\n\n✦ DESIGN\n• Skull and lightning bolt artwork — peak thrash aesthetic\n• High-contrast print on dark fabric\n• Inspired by the pioneers of 80s thrash metal\n\n✦ SPECS\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring hood\n• One-piece body construction\n• Ethically manufactured\n\n✦ WHO NEEDS THIS\n→ Thrash metal loyalists\n→ 80s metal nostalgia enthusiasts\n→ Anyone who needs a hoodie as intense as their playlist\n\n🖤 Deathlipse — thrashing since forever.",
        "tags": ["thrash metal hood", "80s metal hoodie", "skull lightning", "heavy metal gift", "gothic rock hoodie", "metal band merch", "concert hoodie", "metalhead pullover", "electric skull art", "alt sweatshirt", "dark art hoodie", "rock gift him", "festival hoodie"]
    },
    # Lamb of God Hoodie
    {
        "id": 1845884440,
        "title": "Lamb of God Inspired Hoodie | Groove Metal Band Pullover | Skull Artwork Sweatshirt | Heavy Metal Gift | Dark Art Hoodie",
        "description": "Pure American metal fury — this Lamb of God-inspired hoodie is for those who worship at the altar of groove.\n\nThe visceral skull artwork channels the relentless aggression and unyielding heaviness that defines one of modern metal's most devastating acts. From the pit to the parking lot, this hoodie is your declaration of allegiance.\n\n✦ THE ARTWORK\n• Aggressive skull design — pure groove metal energy\n• Bold, dark illustration with incredible detail\n• Inspired by modern American metal's finest\n\n✦ BUILT FOR WAR\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket and adjustable drawstring\n• One-piece body — no side seams\n• Ethically sourced, OEKO-TEX certified\n\n✦ FOR THOSE WHO\n→ Live for the breakdown\n→ Need concert-tested comfort\n→ Want to gift the ultimate modern metal piece\n\n🖤 Deathlipse — walk with me in hell.",
        "tags": ["groove metal hoodie", "skull art hoodie", "heavy metal gift", "dark art pullover", "metal band merch", "concert hoodie", "metalhead gift", "american metal", "death metal hoodie", "alt fashion", "gothic hoodie", "band sweatshirt", "aggressive merch"]
    },
    # Slipknot-style Hoodie
    {
        "id": 1845876652,
        "title": "Nu Metal Mask Art Hoodie | Dark Carnival Pullover | Heavy Metal Band Sweatshirt | Gothic Horror Gift | Underground Merch",
        "description": "Welcome to the dark carnival — this mask-art hoodie channels the chaotic, theatrical energy of nu metal's most terrifying act.\n\nThe haunting mask imagery captures the theatrical darkness and visceral intensity that redefined heavy music in the late 90s. This hoodie is for the nine who never backed down and the fans who stood with them.\n\n✦ DESIGN\n• Dark carnival mask-inspired artwork\n• Theatrical horror meets metal aggression\n• Bold, unsettling, impossible to ignore\n\n✦ QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• Double-lined hood for extra warmth\n• Ethically manufactured\n\n✦ PERFECT FOR\n→ Nu metal and industrial metal fans\n→ Horror-themed fashion enthusiasts\n→ Concert warriors and festival-goers\n\n🖤 Deathlipse — we are not your kind.",
        "tags": ["nu metal hoodie", "mask art hoodie", "dark carnival", "horror metal hood", "gothic sweatshirt", "heavy metal gift", "underground merch", "metalhead hoodie", "concert pullover", "dark art hoodie", "alt fashion", "band merch", "industrial metal"]
    },
    # Slayer-style Hoodie
    {
        "id": 1845891360,
        "title": "Thrash Metal Pentagram Hoodie | 80s Metal Band Pullover | Dark Occult Art Sweatshirt | Heavy Metal Gift | Gothic Hoodie",
        "description": "RAINING BLOOD on basic hoodies — this pentagram thrash metal pullover is pure 80s fury.\n\nInspired by the darkest, fastest, most unrelenting chapter of thrash metal history, this hoodie features occult-infused artwork that captures the blasphemous beauty of a genre that refused to be silenced. If your playlist starts with S and ends with devastation, this is your uniform.\n\n✦ DESIGN\n• Pentagram and occult-inspired thrash artwork\n• Bold, dark, confrontational graphic\n• A tribute to 80s thrash metal's darkest chapter\n\n✦ SPECS\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• One-piece body, no side seams\n• Ethically sourced\n\n✦ FOR FANS WHO\n→ Know the big four by heart\n→ Need their fashion as aggressive as their music\n→ Want to gift pure thrash metal darkness\n\n🖤 Deathlipse — reign in style.",
        "tags": ["thrash metal hood", "pentagram hoodie", "80s metal band", "occult art hoodie", "heavy metal gift", "gothic hoodie", "metal band merch", "dark art pullover", "concert hoodie", "metalhead gift", "slayer inspired", "alt fashion", "aggressive merch"]
    },
    # Bring Me The Horizon Hoodie
    {
        "id": 1845800508,
        "title": "BMTH Inspired Metal Hoodie | Post Metalcore Pullover | Amo Dark Art Sweatshirt | Alternative Rock Gift | Unisex Band Merch",
        "description": "Can you feel my heart? This BMTH-inspired hoodie bridges metalcore fury with post-genre dark art.\n\nFrom deathcore roots to genre-defying evolution, this hoodie captures the visual language of one of modern rock's most transformative acts. The artwork blends elements of post-metalcore aesthetics with dark, atmospheric imagery — perfect for fans who evolve with their music.\n\n✦ DESIGN\n• Post-metalcore dark art illustration\n• Genre-crossing visual aesthetic\n• Bold, modern, instantly recognizable\n\n✦ QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• Premium construction throughout\n• Ethically manufactured\n\n✦ WHO IT'S FOR\n→ Metalcore and post-hardcore fans\n→ Alternative rock lovers who appreciate evolution\n→ A gift for the fan who's grown with the band\n\n🖤 Deathlipse — evolving in the dark.",
        "tags": ["bmth hoodie", "metalcore merch", "post metal hoodie", "alt rock gift", "dark art pullover", "band merch hoodie", "unisex hoodie", "concert hoodie", "emo sweatshirt", "heavy music gift", "modern metal", "gothic pullover", "festival hoodie"]
    },
    # Opeth Design Full-Zip Hoodie
    {
        "id": 1839624983,
        "title": "Opeth Full Zip Hoodie | Progressive Metal Band Jacket | Gothic Rock Sweatshirt | Dark Art Metalhead Gift | Unisex Zip Up",
        "description": "Zip into the darkness with this Opeth-inspired full zip hoodie — progressive metal's finest, now in jacket form.\n\nUnlike a pullover, this full-zip design gives you layering freedom while showcasing the haunting Opeth-inspired artwork front and center. Perfect for throwing on over a band tee before a show or as your daily armor against the ordinary.\n\n✦ DESIGN\n• Opeth-inspired gothic metal illustration\n• Full front graphic with complementary detail\n• Premium print quality — vivid and fade-resistant\n\n✦ FEATURES\n• Full-length quality zipper\n• Two side pockets for warmth\n• Adjustable drawstring hood\n• Premium cotton-poly blend\n• Unisex fit — see our size chart\n\n✦ VERSATILE STYLING\n→ Layer over any band tee for instant cool\n→ Lightweight for indoor venues, warm for outdoor\n→ The perfect transitional jacket\n\n🖤 Deathlipse — zip up, tune out, turn it up.",
        "tags": ["opeth zip hoodie", "prog metal jacket", "full zip hoodie", "metal band zip up", "gothic sweatshirt", "dark art zip up", "metalhead gift", "unisex band hood", "concert jacket", "death metal merch", "rock zip hoodie", "alt fashion", "music lover gift"]
    },
    # Bring Me The Horizon Stencil Hoodie
    {
        "id": 1845815990,
        "title": "BMTH Stencil Art Hoodie | Metalcore Band Pullover | Dark Aesthetic Sweatshirt | Alternative Rock Gift | Gothic Band Merch",
        "description": "Spray-painted rebellion — this BMTH stencil art hoodie brings street-level edge to your metalcore wardrobe.\n\nThe raw stencil-style graphic captures the DIY spirit that runs through the veins of alternative culture. It's where concert energy meets street art aesthetics — bold, confrontational, and unapologetically underground.\n\n✦ DESIGN\n• Stencil-style graphic — raw, urban, edgy\n• Street art meets metalcore aesthetics\n• Perfect for fans who live between genres\n\n✦ QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• One-piece construction\n• Ethically manufactured\n\n✦ FOR\n→ BMTH fans and metalcore enthusiasts\n→ Street art and alternative culture lovers\n→ A gift with serious edge\n\n🖤 Deathlipse — art from the underground.",
        "tags": ["bmth stencil hood", "metalcore pullover", "dark aesthetic", "alt rock gift", "gothic band merch", "street art hoodie", "band sweatshirt", "unisex hoodie", "concert merch", "emo hoodie", "heavy music gift", "modern metal hood", "underground wear"]
    },
    # Avenged Sevenfold Hoodie
    {
        "id": 1845864976,
        "title": "A7X Inspired Metal Hoodie | Dark Angel Art Pullover | Heavy Metal Band Sweatshirt | Gothic Skull Gift | Rock Merch Unisex",
        "description": "Hail to the King — this A7X-inspired hoodie channels the dark grandeur of heavy metal's modern royalty.\n\nThe haunting angel-of-death artwork captures the epic, cinematic scale of modern heavy metal. Bold wings, skull motifs, and gothic grandeur merge into a design worthy of headlining any arena.\n\n✦ DESIGN\n• Dark angel artwork — epic, cinematic, bold\n• Gothic elements with modern metal edge\n• A design as grand as the music it represents\n\n✦ QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• One-piece construction, no side seams\n• Ethically sourced\n\n✦ PERFECT FOR\n→ Fans of modern heavy metal anthems\n→ Gothic and dark art fashion lovers\n→ A gift fit for metal royalty\n\n🖤 Deathlipse — seize the day, wear the night.",
        "tags": ["a7x hoodie", "dark angel art", "heavy metal hoodie", "gothic skull gift", "rock merch unisex", "metal band merch", "concert hoodie", "metalhead pullover", "death bat art", "alt sweatshirt", "band gift him", "modern metal", "festival hoodie"]
    },
    # Rammstein Hoodie
    {
        "id": 1845854310,
        "title": "Rammstein Inspired Hoodie | Industrial Metal Band Pullover | German Rock Sweatshirt | Dark Art Fire Gift | Gothic Merch",
        "description": "Feuer frei! This Rammstein-inspired hoodie brings industrial metal's most explosive act to your wardrobe.\n\nThe fierce artwork channels the fire, controversy, and theatrical darkness that defines Germany's most famous metal export. From Wembley to your wardrobe, this hoodie burns with the intensity of a live Rammstein show.\n\n✦ DESIGN\n• Fire-and-darkness inspired graphic\n• Industrial metal aesthetic at its boldest\n• A tribute to German precision and fury\n\n✦ CONSTRUCTION\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• Premium print, ethically manufactured\n• OEKO-TEX certified dyes\n\n✦ FOR THOSE WHO\n→ Live for Du Hast and Sonne\n→ Appreciate industrial art and pyro\n→ Want to gift the ultimate industrial metal piece\n\n🖤 Deathlipse — we all burn bright.",
        "tags": ["industrial metal", "german metal band", "fire art hoodie", "gothic merch", "dark art pullover", "heavy metal gift", "metal band hoodie", "concert hoodie", "metalhead gift", "rock sweatshirt", "NDH hoodie", "alt fashion", "european metal"]
    },
    # Opeth Skull T-Shirt
    {
        "id": 1668443014,
        "title": "Opeth Skull Art T-Shirt | Progressive Metal Graphic Tee | Gothic Rock Band Merch | Dark Art Unisex Shirt | Metalhead Gift",
        "description": "Skulls and shadows — this Opeth-inspired tee captures the beautiful brutality of progressive metal.\n\nThe intricate skull artwork channels the dark, atmospheric beauty that has made Opeth one of metal's most revered acts. Printed on premium soft fabric, this tee is both a visual statement and an all-day comfort piece.\n\n✦ DESIGN\n• Opeth-inspired skull illustration — intricate, dark, beautiful\n• Fade-resistant, eco-friendly inks\n• Art that captures the essence of prog metal\n\n✦ FIT & QUALITY\n• Premium unisex tee — soft and breathable\n• True to size — see our chart\n• Pre-shrunk for consistent fit\n\n✦ FOR\n→ Prog metal devotees and dark art lovers\n→ Concert-ready or everyday wear\n→ A refined gift for a discerning metalhead\n\n🖤 Deathlipse — wear the depth.",
        "tags": ["opeth skull tee", "prog metal shirt", "gothic rock merch", "dark art tshirt", "metalhead gift", "band graphic tee", "skull art shirt", "unisex metal tee", "concert shirt", "death metal tee", "alt clothing", "heavy metal tee", "music fan gift"]
    },
    # Opeth Vintage T-Shirt
    {
        "id": 1668445614,
        "title": "Opeth Vintage Style T-Shirt | Retro Metal Band Tee | Gothic Art Graphic Shirt | Progressive Rock Gift | Dark Unisex Tee",
        "description": "Vintage vibes, modern darkness — this retro Opeth-inspired tee looks like you've been a fan since day one.\n\nThe faded, vintage-style design gives this tee the look and feel of a concert souvenir you've treasured for decades. Worn-in aesthetic, brand new quality — the best of both worlds.\n\n✦ DESIGN\n• Vintage-inspired Opeth aesthetic\n• Faded, worn-in look from day one\n• Retro concert tee vibes\n\n✦ QUALITY\n• Premium unisex soft cotton blend\n• Fade-resistant printing\n• Pre-shrunk, true to size\n\n✦ PERFECT FOR\n→ Vintage band tee collectors\n→ Fans who want that authentic worn-in look\n→ Gifting to a long-time metal devotee\n\n🖤 Deathlipse — timeless darkness.",
        "tags": ["opeth vintage tee", "retro metal shirt", "gothic art tshirt", "prog rock gift", "dark unisex tee", "band merch shirt", "vintage band tee", "metalhead gift", "concert shirt", "90s metal look", "alt clothing", "heavy metal tee", "music lover tee"]
    },
    # Motionless In White Hoodie
    {
        "id": 1845843392,
        "title": "MIW Inspired Gothic Hoodie | Metalcore Band Pullover | Dark Horror Art Sweatshirt | Goth Rock Gift | Alternative Merch",
        "description": "Gothic horror meets metalcore fury — this MIW-inspired hoodie is for those who paint their darkness in detail.\n\nChanneling the theatrical, horror-infused aesthetic of modern gothic metalcore, this hoodie features dark artwork that bridges the gap between classic gothic imagery and contemporary heavy music.\n\n✦ DESIGN\n• Gothic horror-inspired illustration\n• Theatrical dark art meets metalcore energy\n• Detailed, haunting, conversation-starting\n\n✦ QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• Premium construction, ethically made\n\n✦ WHO IT'S FOR\n→ Gothic metalcore and horror rock fans\n→ Dark fashion and theatrical music lovers\n→ The perfect gift for the goth in your life\n\n🖤 Deathlipse — creatures of the night.",
        "tags": ["gothic metalcore", "horror art hoodie", "goth rock gift", "alt merch hoodie", "dark art pullover", "band sweatshirt", "metalhead hoodie", "concert hoodie", "emo gothic wear", "heavy music gift", "theatrical metal", "underground merch", "modern goth"]
    },
    # Opeth Mug 3
    {
        "id": 1862028393,
        "title": "Opeth Dark Art Mug | Heavy Metal Coffee Cup | Gothic Band Ceramic | Progressive Rock Home | Metalhead Kitchen Gift",
        "description": "Every sip, steeped in darkness — this Opeth-inspired mug brings progressive metal to your morning ritual.\n\nDark, atmospheric artwork wraps around this premium ceramic mug, turning your coffee break into an art gallery moment. For fans who take their music — and their coffee — dark.\n\n✦ SPECS\n• Premium ceramic\n• Glossy finish, vivid colors\n• Microwave and dishwasher safe\n• 11oz capacity\n• Comfortable C-handle\n\n✦ GIFT-WORTHY\n→ For the metalhead who has everything\n→ Gothic kitchen collectors\n→ Anyone who needs darkness with breakfast\n\n🖤 Deathlipse — dark art, daily ritual.",
        "tags": ["opeth dark mug", "metal coffee cup", "gothic ceramic mug", "prog rock home", "metalhead kitchen", "band merch mug", "heavy metal cup", "dark art mug", "goth home decor", "music lover mug", "unique mug gift", "alt home decor", "coffee lover"]
    },
    # Black Sabbath style Hoodie
    {
        "id": 1860972283,
        "title": "Doom Metal Occult Hoodie | 70s Heavy Metal Band Pullover | Gothic Sabbath Art Sweatshirt | Dark Witch Gift | Classic Rock Merch",
        "description": "The riff that started it all — this doom metal hoodie channels the dark genesis of heavy music.\n\nInspired by the occult imagery and crushing riffs that birthed an entire genre, this hoodie features dark, witchcraft-infused artwork that pays homage to the pioneers of doom. If heavy metal has a church, this is the vestment.\n\n✦ DESIGN\n• Occult doom metal artwork — dark, mystical, iconic\n• 70s heavy metal visual influence\n• A tribute to the birth of the genre\n\n✦ QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket, adjustable drawstring\n• Ethically manufactured\n\n✦ FOR THE DEVOTED\n→ Doom and classic metal worshippers\n→ Occult art and dark fashion enthusiasts\n→ Fans of the heaviest riff ever written\n\n🖤 Deathlipse — heavy since the beginning.",
        "tags": ["doom metal hoodie", "70s metal band", "occult art hoodie", "gothic sabbath", "dark witch hoodie", "classic rock merch", "heavy metal gift", "metalhead pullover", "vintage metal", "concert hoodie", "alt fashion", "dark art hoodie", "stoner metal"]
    },
    # Opeth Women T-Shirt
    {
        "id": 1699215311,
        "title": "Opeth Peacock Skull T-Shirt | Progressive Metal Art Tee | Gothic Fantasy Graphic | Death Metal Gift | Dark Art Unisex Shirt",
        "description": "Where beauty decays and skulls bloom — this Opeth-inspired peacock tee is progressive metal's most haunting visual.\n\nA majestic peacock stands sentinel over a pile of skulls and bones, capturing the duality that defines Opeth's music — beauty and brutality, life and death. This intricate design is a wearable masterpiece.\n\n✦ DESIGN\n• Peacock and skull artwork\n• Rich detail and vibrant color\n• Dark fantasy art on premium cotton\n\n✦ QUALITY\n• Premium unisex tee\n• Fade-resistant print\n• True to size, pre-shrunk\n\n✦ FOR\n→ Prog metal fans who appreciate visual art\n→ A gift-worthy tee for discerning metalheads\n\n🖤 Deathlipse — beauty meets brutality.",
        "tags": ["opeth tshirt", "peacock skull tee", "prog metal shirt", "gothic fantasy art", "death metal gift", "dark art tee", "metalhead gift", "occult fashion", "morbid art shirt", "heavy metal tee", "90s metal band", "band merch tee", "alt shirt"]
    },
]

def update_listing(listing_id, title, description, tags):
    url = f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}"
    data = {"title": title, "description": description}
    for i, tag in enumerate(tags[:13]):
        data[f"tags[{i}]"] = tag
    resp = requests.patch(url, headers=HEADERS, data=data)
    return resp.status_code, resp.text

def main():
    total = len(OPTIMIZED)
    success = 0
    failed = 0
    print(f"{'='*60}")
    print(f"ETSY OPTIMIZER BATCH 2 - Fixes + Remaining Listings")
    print(f"Optimizing {total} listings...")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(OPTIMIZED):
        lid = item["id"]
        title = item["title"]
        desc = item["description"]
        tags = item["tags"]
        
        # Validate tags
        bad_tags = [t for t in tags if len(t) > 20]
        if bad_tags:
            print(f"[{i+1}/{total}] SKIPPING {lid} - tags too long: {bad_tags}")
            failed += 1
            continue
        
        print(f"[{i+1}/{total}] Updating: {title[:60]}...")
        status, response = update_listing(lid, title, desc, tags)
        
        if status == 200:
            print(f"  SUCCESS (HTTP {status})")
            success += 1
        else:
            print(f"  FAILED (HTTP {status}): {response[:200]}")
            failed += 1
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"BATCH 2 COMPLETE!")
    print(f"Success: {success}/{total}")
    print(f"Failed: {failed}/{total}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
