"""
Etsy Listing Optimizer - Deathlipse Shop
Tüm ürünleri SEO açısından maksimum seviyeye çıkarır.
Değişen: title, description, tags
"""
import json
import requests
import time
import sys

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

# ============================================================
# OPTIMIZED LISTINGS DATA
# Each listing: id, new_title, new_description, new_tags
# ============================================================

OPTIMIZED = [
    # 1) Opeth Band Hoodie
    {
        "id": 1668436486,
        "title": "Opeth Band Hoodie | Progressive Metal Pullover Sweatshirt | Gothic Rock Gift for Him Her | Dark Art Unisex Hoodie",
        "description": "Channel the haunting beauty of progressive metal with this Opeth-inspired hoodie — where dark art meets everyday comfort.\n\nThis isn't just merch. It's a statement piece for fans who live and breathe the atmospheric, genre-defying sound of one of metal's most revered acts. The bold graphic captures Opeth's signature blend of beauty and brutality, making it an instant conversation starter at shows, festivals, or anywhere you want your passion heard.\n\n✦ WHY YOU'LL LOVE IT\n• Spacious kangaroo pouch pocket keeps hands warm between sets\n• Adjustable drawstring hood for that low-profile, mysterious look\n• Knitted in one piece — no side seams for a clean, premium silhouette\n• 50% US-grown cotton / 50% polyester — soft, warm, built to last\n• Ethically made with 100% US-grown cotton (Gildan, OEKO-TEX certified)\n\n✦ PERFECT FOR\n→ Concert nights & music festivals\n→ Casual layering with your favorite band tee\n→ A gift any metalhead will treasure\n\n✦ CARE INSTRUCTIONS\n• Machine wash cold (max 30°C / 90°F)\n• Tumble dry medium\n• Iron on low heat\n• Do not dry clean\n• Non-chlorine bleach as needed\n\n✦ SIZING: Unisex fit — check the size chart in our photos for the perfect fit.\n\nShip worldwide from the USA. Made to order — please allow 3-5 business days for production.\n\n🖤 More dark designs at Deathlipse — your home for underground metal fashion.",
        "tags": ["opeth hoodie", "progressive metal", "metal band hoodie", "gothic rock gift", "metalhead gift him", "dark art hoodie", "unisex band hoodie", "concert hoodie", "death metal merch", "music lover gift", "alternative clothing", "heavy metal fashion", "festival hoodie"]
    },
    # 2) Gothic Skull Design Sneakers
    {
        "id": 1861644349,
        "title": "Gothic Skull High Top Sneakers | Dark Art Canvas Shoes | Metalhead Streetwear | Goth Punk Rock Shoes Unisex Gift",
        "description": "Walk on the dark side with these skull-adorned high-top sneakers — where gothic art meets streetwear edge.\n\nEvery step makes a statement. These canvas high-tops feature an intricate gothic skull design that channels the raw energy of the underground metal scene. Whether you're hitting a show, skating through the city, or simply refusing to blend in, these shoes were built for those who wear their darkness proudly.\n\n✦ DESIGN DETAILS\n• Hand-finished gothic skull artwork with intricate shading\n• Dark colorway that pairs with everything in your alternative wardrobe\n• High-top silhouette for that classic punk-rock aesthetic\n\n✦ CONSTRUCTION\n• Durable canvas upper for breathability and comfort\n• Cushioned insole for all-day wear\n• Non-slip rubber sole with excellent grip\n• Metal eyelets and reinforced stitching\n\n✦ PERFECT FOR\n→ Concerts, festivals & everyday wear\n→ Gift for the goth, punk, or metalhead in your life\n→ Unique alternative to mainstream sneakers\n\n✦ SIZING: Unisex — see our size chart for accurate fit.\n\n🖤 Explore more dark designs at Deathlipse — underground fashion for underground souls.",
        "tags": ["gothic sneakers", "skull high tops", "goth shoes", "punk rock shoes", "metalhead sneakers", "dark art shoes", "alternative footwear", "gothic gift him her", "skull canvas shoes", "y2k goth shoes", "edgy streetwear", "occult fashion", "unisex goth shoes"]
    },
    # 3) Coffin Skeleton Printed T-Shirt
    {
        "id": 1670982348,
        "title": "Coffin Skeleton T-Shirt | Gothic Horror Graphic Tee | Skull Dark Art Shirt | Death Metal Unisex Gift | Macabre Fashion",
        "description": "Rise from the grave in style — this coffin skeleton tee is pure gothic horror art you can wear.\n\nFeaturing a hauntingly detailed skeleton emerging from a coffin amidst a sea of skulls, this graphic tee captures the raw essence of death metal aesthetics. The twisted, macabre artwork is printed with vivid detail that won't fade, making it a wardrobe staple for anyone who thrives in the shadows.\n\n✦ DESIGN\n• Detailed coffin skeleton artwork — dark, bold, unforgettable\n• Printed with eco-friendly, fade-resistant inks\n• Designed for fans of horror, metal, and the macabre\n\n✦ FABRIC & FIT\n• Premium cotton-poly blend for softness and durability\n• Unisex relaxed fit — true to size\n• Pre-shrunk to maintain shape wash after wash\n• Lightweight and breathable for all-day comfort\n\n✦ GREAT FOR\n→ Concert nights, casual wear, or layering under flannels\n→ A killer gift for metalheads, horror fans & goth enthusiasts\n→ Halloween, birthday, or just because they're awesome\n\n🖤 Deathlipse — wear the darkness.",
        "tags": ["coffin skeleton tee", "gothic horror shirt", "skull graphic tee", "death metal shirt", "macabre fashion", "dark art tshirt", "goth clothing", "horror tee gift", "occult tshirt", "metalhead gift", "black metal style", "halloween shirt", "alternative tee"]
    },
    # 4) Deathlipse Logo T-shirt
    {
        "id": 1678353121,
        "title": "Deathlipse Logo T-Shirt | Gothic Skull Moon Eclipse Tee | Dark Aesthetic Occult Graphic | Unisex Alternative Clothing",
        "description": "Wear the eclipse — the official Deathlipse skull-moon logo tee for those who walk between worlds.\n\nThis isn't just a t-shirt — it's the emblem of Deathlipse. The haunting skull-moon eclipse design speaks to those who find beauty in darkness, who hear the call of the underground. Bold enough to stand alone, subtle enough to layer, this tee is the cornerstone of any alternative wardrobe.\n\n✦ THE DESIGN\n• Original Deathlipse eclipse skull logo\n• Intricate gothic linework with cosmic elements\n• A symbol for the bold, the dark, the unapologetic\n\n✦ FABRIC & FIT\n• Gildan Softstyle — buttery soft ringspun cotton\n• Unisex relaxed fit for effortless comfort\n• Pre-shrunk and side-seamed for a tailored look\n• Available in multiple sizes — check our chart\n\n✦ PERFECT FOR\n→ Daily wear for alternative fashion lovers\n→ Layering under hoodies, flannels, or jackets\n→ An iconic gift for anyone in the goth/metal scene\n\n🖤 This is Deathlipse. Wear the darkness. Own the night.",
        "tags": ["deathlipse tshirt", "gothic skull tee", "moon eclipse shirt", "dark aesthetic tee", "occult graphic tee", "alternative clothing", "goth fashion", "unisex graphic tee", "skull moon shirt", "underground fashion", "esoteric apparel", "black metal tee", "dark art shirt"]
    },
    # 5) Baby Metal Heavy Metal Hoodie
    {
        "id": 4381602553,
        "title": "Babymetal Inspired Hoodie | Kawaii Metal Band Pullover | Japanese Rock Sweatshirt | Gothic Anime Gift | Metalhead Hoodie",
        "description": "Where kawaii meets metal — this Babymetal-inspired hoodie fuses Japanese pop culture with heavyweight dark art.\n\nBorn from the collision of J-pop and death metal, this hoodie captures the electrifying energy of the kawaii metal movement. The striking graphic blends anime-inspired elements with dark fantasy motifs, creating a wearable piece of art that's as unique as the genre itself.\n\n✦ WHAT MAKES IT SPECIAL\n• Babymetal-inspired dark fantasy illustration\n• Bold, eye-catching graphic that sparks conversation\n• Bridges anime fandom and metal culture in one piece\n\n✦ QUALITY & COMFORT\n• 50% cotton / 50% polyester heavy blend\n• Spacious kangaroo pocket for warmth\n• Adjustable drawstring hood\n• Ethically sourced US-grown cotton, OEKO-TEX certified dyes\n\n✦ IDEAL FOR\n→ Babymetal fans & J-rock enthusiasts\n→ Anime conventions & metal festivals\n→ A unique gift for someone who defies genre boundaries\n\n✦ SIZING: Unisex classic fit — see our size chart photos.\n\n🖤 Deathlipse — where underground fashion meets otherworldly art.",
        "tags": ["babymetal hoodie", "kawaii metal merch", "japanese metal band", "anime metal hoodie", "gothic lolita", "j-rock hoodie", "metalhead gift", "dark art hoodie", "alternative fashion", "heavy metal pullover", "concert sweatshirt", "idol metal merch", "goth anime gift"]
    },
    # 6) Arch-Enemy Heavy Metal Hoodie
    {
        "id": 1860991651,
        "title": "Arch Enemy Inspired Hoodie | Melodic Death Metal Sweatshirt | Gothic Warrior Art | Swedish Metal Band Pullover Gift",
        "description": "Unleash your inner warrior with this Arch Enemy-inspired hoodie — fierce, dark, and utterly unapologetic.\n\nChanneling the raw power of Swedish melodic death metal, this hoodie features a striking warrior illustration surrounded by occult symbols. The fierce feminine energy and dark mysticism captured in the design pay tribute to one of metal's most iconic frontwomen and the genre-defining sound that changed extreme music forever.\n\n✦ THE ARTWORK\n• Warrior goddess illustration with raven and occult symbols\n• Captures the fierce spirit of melodic death metal\n• Dark, detailed, and museum-quality print\n\n✦ BUILT TO LAST\n• 50% US-grown cotton / 50% polyester heavy blend\n• Kangaroo pocket and adjustable drawstring hood\n• One-piece construction — no side seams\n• OEKO-TEX certified, ethically manufactured\n\n✦ PERFECT GIFT FOR\n→ Fans of Swedish death metal and extreme music\n→ Anyone who wears their rebellion on their sleeve\n→ Concerts, festivals, and everyday dark fashion\n\n🖤 Deathlipse — forged in darkness, worn with pride.",
        "tags": ["arch enemy hoodie", "melodic death metal", "swedish metal band", "warrior hoodie", "gothic metal hoodie", "extreme metal merch", "metalhead gift him", "dark art pullover", "occult hoodie", "band merch hoodie", "concert sweatshirt", "heavy metal fashion", "alternative hoodie"]
    },
    # 7) Opeth Sorceress Mug
    {
        "id": 1861938559,
        "title": "Opeth Sorceress Mug | Peacock Skull Art Coffee Cup | Gothic Home Decor | Metalhead Gift | Dark Fantasy Ceramic Mug",
        "description": "Start your morning ritual with a vessel worthy of a sorceress — this Opeth-inspired mug turns every sip into dark art.\n\nThe majestic peacock spreads its vibrant plumage over a haunting tableau of skulls, capturing the signature aesthetic of progressive metal's finest. This ceramic mug brings gallery-worthy dark fantasy art to your morning coffee, afternoon tea, or late-night studio session.\n\n✦ DESIGN DETAILS\n• Peacock and skull artwork inspired by the Sorceress era\n• Rich, vibrant colors that pop against the dark background\n• Wrap-around print — art from every angle\n\n✦ MUG SPECS\n• Premium ceramic construction\n• Glossy finish for vivid color reproduction\n• Microwave and dishwasher safe\n• Comfortable C-handle grip\n• 11oz standard capacity\n\n✦ MAKES AN INCREDIBLE GIFT FOR\n→ Progressive metal fans & Opeth devotees\n→ Gothic home decor enthusiasts\n→ Anyone who takes their coffee as dark as their music\n\n🖤 Deathlipse — dark art for every corner of your life.",
        "tags": ["opeth mug", "metal coffee mug", "gothic home decor", "peacock skull art", "metalhead gift", "dark fantasy mug", "progressive metal", "band merch mug", "goth coffee cup", "heavy metal gifts", "occult home decor", "music lover mug", "sorceress art"]
    },
    # 8) Pan tera Heavy Metal Hoodie (Skull & Snake)
    {
        "id": 4513162562,
        "title": "Groove Metal Skull Snake Hoodie | 90s Heavy Metal Sweatshirt | Southern Rock Band Pullover | Dark Art Gothic Gift",
        "description": "Coil into the darkness with this skull-and-snake hoodie — a tribute to the raw, unrelenting power of 90s groove metal.\n\nThe graphic print showcases a haunting skull entwined with serpents, capturing the dark, aggressive aesthetic that defined an entire era of heavy metal. This hoodie doesn't just pay homage — it embodies the spirit of rebellion, sonic fury, and unapologetic intensity.\n\n✦ THE ARTWORK\n• Skull and snake graphic — iconic groove metal imagery\n• Bold, high-contrast print that commands attention\n• Inspired by the golden age of 90s metal\n\n✦ PREMIUM CONSTRUCTION\n• 50% cotton / 50% polyester heavy blend (8.0 oz/yd²)\n• Kangaroo pocket and color-matched drawcord\n• Double-lined hood for extra warmth\n• Ethically sourced, OEKO-TEX certified\n\n✦ WHO IT'S FOR\n→ Fans of groove metal, thrash, and southern rock\n→ Concert-goers, festival warriors, everyday rebels\n→ A sick gift for the metalhead who has everything\n\n🖤 Deathlipse — forged in the pit, worn on the street.",
        "tags": ["groove metal hoodie", "skull snake hoodie", "90s metal hoodie", "southern metal band", "dark art hoodie", "heavy metal gift", "gothic pullover", "metalhead hoodie", "thrash metal merch", "skull graphic hoodie", "rock band hoodie", "grunge hoodie", "concert sweatshirt"]
    },
    # 9) Pan-teraaa Metal Band Hoodie
    {
        "id": 4513162561,
        "title": "Groove Metal Band Hoodie | Vintage Thrash Metal Pullover | 90s Rock Sweatshirt | Heavy Metal Unisex Gift | Dark Fashion",
        "description": "Throw back to the heaviest decade in metal history with this vintage-inspired groove metal hoodie.\n\nDesigned for those who grew up on crushing riffs and pit-ready breakdowns, this hoodie channels the raw intensity of 90s thrash and groove metal. The bold band-style graphic print is a love letter to the era that gave metal its meanest edge.\n\n✦ DESIGN\n• Vintage-inspired metal band graphic\n• High-contrast print on premium fabric\n• Captures the raw spirit of 90s metal\n\n✦ QUALITY DETAILS\n• 50% US-grown cotton / 50% polyester (8.0 oz/yd²)\n• Classic fit with kangaroo pouch pocket\n• Color-matched drawcord and double-lined hood\n• Tear-away label for itch-free comfort\n• OEKO-TEX certified dyes — low environmental impact\n\n✦ PERFECT FOR\n→ Metal shows, tailgates, and everyday wear\n→ A timeless gift for thrash and groove metal fans\n→ Layering with your favorite band tee\n\n✦ SIZING: Unisex — see size chart in photos.\n\n🖤 Deathlipse — underground fashion, overground quality.",
        "tags": ["groove metal hoodie", "vintage metal band", "thrash metal merch", "90s rock hoodie", "heavy metal pullover", "unisex band hoodie", "dark fashion hoodie", "metalhead gift", "concert hoodie", "grunge sweatshirt", "rock merch hoodie", "alternative hoodie", "festival wear"]
    },
    # 10) Heavy Metal Anime T-Shirt (Nana)
    {
        "id": 1890009888,
        "title": "Nana Anime Tank Top | Black Stones Band Graphic | Y2K Goth Crop Top | Japanese Anime Gift | Dark Aesthetic Women's Tee",
        "description": "Channel your inner Nana Osaki with this Black Stones tank top — where anime rebellion meets Y2K goth style.\n\nInspired by the cult-classic anime series, this retro graphic tank features the legendary Black Stones band design. It's the perfect piece for fans who see themselves in Nana's fearless, rock-and-roll spirit. Layer it under a leather jacket or wear it solo — either way, you're making a statement.\n\n✦ THE DESIGN\n• Black Stones / BLAST band retro graphic\n• Faded vintage aesthetic for authentic Y2K vibes\n• A must-have for any Nana anime collection\n\n✦ FIT & FABRIC\n• 52% Airlume combed ringspun cotton / 48% polyester\n• Chunky spaghetti straps for a bold silhouette\n• Mid-length crop — perfect for layering or standing alone\n• Soft, breathable, and socially conscious production\n\n✦ GREAT FOR\n→ Anime conventions, concerts, and festivals\n→ Y2K / goth / alternative daily outfits\n→ A unique gift for Nana fans and anime lovers\n\n🖤 Deathlipse — where anime meets the underground.",
        "tags": ["nana anime tank top", "black stones shirt", "y2k goth top", "anime band merch", "japanese anime gift", "dark aesthetic tee", "kawaii goth fashion", "retro anime shirt", "alt fashion women", "concert crop top", "anime cosplay tee", "gothic anime wear", "music anime merch"]
    },
    # 11) Opeth Women's Tank Top
    {
        "id": 1792122708,
        "title": "Opeth Women's Tank Top | Gothic Metal Racerback | Dark Art Band Tee | Progressive Metal Gift | Concert Festival Top",
        "description": "Embrace the darkness in style with this Opeth-inspired women's tank top — designed for fans who live between beauty and brutality.\n\nThis isn't just another band tank. The gothic design captures Opeth's signature blend of progressive complexity and dark atmosphere, printed on a premium racerback that moves with you from festival grounds to midnight streets.\n\n✦ DESIGN\n• Opeth-inspired gothic metal artwork\n• Bold, detailed print that holds up wash after wash\n• Made for fans of progressive and gothic metal\n\n✦ FIT & FABRIC\n• Luxurious soft fabric with a flattering feminine cut\n• Chunky spaghetti straps for comfort and style\n• Breathable and lightweight — perfect for hot venues\n• Available in multiple sizes — check our chart\n\n✦ STYLE IT\n→ Solo at summer festivals and outdoor shows\n→ Layered under a flannel, leather jacket, or cardigan\n→ Paired with high-waist jeans and boots for a killer look\n\n✦ GIFT-WORTHY: Comes looking amazing — perfect for birthdays, holidays, or \"just because\" for the metalhead in your life.\n\n🖤 Deathlipse — dark art, worn beautifully.",
        "tags": ["opeth tank top", "metal women tank", "gothic racerback", "concert festival top", "progressive metal", "band tee women", "dark art tank", "metalhead gift her", "goth summer top", "y2k metal fashion", "rock music tank", "alt clothing women", "gothic metal gift"]
    },
    # 12) Daddylica Grill Master T-Shirt
    {
        "id": 4307080679,
        "title": "Metal BBQ Skull T-Shirt | Grill Master Gift for Dad | Heavy Metal Father's Day Tee | Gothic Barbecue Graphic | Funny Dad Shirt",
        "description": "For the dad who rules the grill AND the mosh pit — this skull BBQ tee is where heavy metal meets backyard legend.\n\nFeaturing a skull wielding a fork and guitar, surrounded by flames, this design is the ultimate crossover between metal culture and grill mastery. It's not just a shirt — it's a badge of honor for dads who season their steaks as hard as their playlists.\n\n✦ THE DESIGN\n• Flaming skull with fork-and-guitar — peak dad metal energy\n• Bold, aggressive artwork with a sense of humor\n• Perfect blend of BBQ culture and heavy metal aesthetics\n\n✦ QUALITY\n• Premium cotton-poly blend for all-day comfort\n• Durable, fade-resistant print\n• Unisex relaxed fit — true to size\n• Pre-shrunk for consistent sizing\n\n✦ THE PERFECT GIFT FOR\n→ Father's Day — the most metal gift he'll get\n→ Birthdays for BBQ-loving metalhead dads\n→ Grillmasters who crank Metallica while flipping burgers\n→ Anyone who believes charcoal > gas\n\n🖤 Deathlipse — even our grills are brutal.",
        "tags": ["metal bbq shirt", "grill master gift", "fathers day metal", "skull bbq tshirt", "funny dad shirt", "gothic barbecue tee", "heavy metal dad", "metalhead dad gift", "bbq skull design", "rock dad tshirt", "dark humor shirt", "metal cooking gift", "punk rock dad"]
    },
    # 13) Five Finger Death Punch Metal Band Hoodie
    {
        "id": 1845793048,
        "title": "Five Finger Death Punch Hoodie | Metal Band Warrior Graphic | Gothic Skull Pullover | Heavy Metal Gift | Unisex Sweatshirt",
        "description": "Unleash your fury with this Five Finger Death Punch-inspired warrior hoodie — built for those who fight through life with fists raised.\n\nThe demonized warrior graphic captures the explosive intensity and unapologetic aggression that defines FFDP's legendary sound. From the pit to the streets, this hoodie is a declaration of war against the ordinary.\n\n✦ THE ARTWORK\n• Demonized warrior with skull and battle imagery\n• Captures the raw energy and rebellion of modern metal\n• Museum-quality print — vivid, detailed, unfading\n\n✦ HOODIE SPECS\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pouch pocket\n• Adjustable drawstring hood\n• One-piece body — no side seams\n• Ethically made with US-grown cotton\n\n✦ MAKES A KILLER GIFT\n→ For FFDP fans and modern metal enthusiasts\n→ Concert nights, gym sessions, or everyday armor\n→ Birthday, holiday, or \"I saw this and thought of you\" gift\n\n🖤 Deathlipse — wear your war paint.",
        "tags": ["ffdp hoodie", "death punch hoodie", "metal band hoodie", "warrior graphic", "gothic skull hoodie", "heavy metal gift", "unisex sweatshirt", "metalhead pullover", "concert hoodie", "aggressive metal", "dark art hoodie", "rock band merch", "nu metal hoodie"]
    },
    # 14) Pantera Cowboy Skeleton Hoodie
    {
        "id": 1845756302,
        "title": "Cowboy Skeleton Metal Hoodie | Southern Rock Gothic Pullover | 90s Groove Metal Sweatshirt | Western Dark Art | Metalhead Gift",
        "description": "Ride into the darkness, partner — this cowboy skeleton hoodie is where southern grit meets gothic metal.\n\nFeaturing a cowboy-hatted skeleton in full western regalia, this hoodie channels the dusty, whiskey-soaked energy of 90s groove metal and southern rock. It's a tribute to the riffs that rattled arenas and the attitude that refused to die.\n\n✦ THE ART\n• Cowboy skeleton graphic — southern gothic at its finest\n• Rich detail with dark western and metal influences\n• A design that tells a story before you say a word\n\n✦ CONSTRUCTION\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket for warmth and convenience\n• Double-lined hood with color-matched drawcord\n• Built tough enough for the road, soft enough for the couch\n\n✦ WHO NEEDS THIS\n→ Fans of groove metal, southern rock, and dark western art\n→ Country-metal crossover enthusiasts\n→ Anyone who wants their hoodie to have as much attitude as they do\n\n🖤 Deathlipse — from the pit to the prairie.",
        "tags": ["cowboy skeleton hoodie", "southern rock hoodie", "groove metal merch", "gothic western art", "90s metal hoodie", "dark cowboy hoodie", "whiskey culture", "metalhead gift", "skeleton hoodie men", "gothic pullover", "country metal", "heavy metal fashion", "alternative hoodie"]
    },
    # 15) Tool Band Hoodie
    {
        "id": 1859941377,
        "title": "Tool Inspired Art Hoodie | Progressive Metal Band Sweatshirt | Psychedelic Dark Art Pullover | Gothic Gift | Unisex Hoodie",
        "description": "Spiral into the unknown with this Tool-inspired hoodie — a wearable piece of psychedelic dark art.\n\nChanneling the mind-bending visuals and philosophical depth of progressive metal's most enigmatic band, this hoodie features artwork that's as layered and complex as the music itself. Sacred geometry, organic forms, and otherworldly imagery merge into a design that rewards closer inspection.\n\n✦ THE ARTWORK\n• Psychedelic-meets-gothic illustration\n• Inspired by the visual language of progressive art metal\n• Intricate details that reveal themselves over time\n\n✦ QUALITY\n• 50% US-grown cotton / 50% polyester\n• Heavy blend (8.0 oz/yd²) for warmth and durability\n• Kangaroo pocket, adjustable drawstring hood\n• One-piece body construction — no side seams\n• OEKO-TEX certified, ethically manufactured\n\n✦ FOR THOSE WHO\n→ Think in odd time signatures\n→ Appreciate art that challenges perception\n→ Want a hoodie as deep as their playlist\n\n🖤 Deathlipse — art for the awakened mind.",
        "tags": ["tool band hoodie", "progressive metal", "psychedelic hoodie", "dark art pullover", "gothic sweatshirt", "art metal merch", "sacred geometry", "metalhead gift", "trippy band hoodie", "alternative fashion", "concert hoodie", "visionary art wear", "spiritual metal"]
    },
    # 16) Opeth Sorceress Mug (second variant - ID 1839624983 if exists, let me check)
    # Actually let me check the remaining IDs from the fetch output

    # 16) Type O Negative Tee
    {
        "id": 1694774434,
        "title": "Type O Negative T-Shirt | Gothic Metal Band Tee | Dark Romantic Album Art | Doom Metal Gift | Unisex Concert Shirt",
        "description": "Bathe in the green glow of gothic doom with this Type O Negative-inspired album art tee.\n\nFor fans who find romance in the darkness and beauty in the heavy, this shirt captures the iconic atmosphere of one of gothic metal's most legendary acts. The album cover print radiates the deep, brooding energy that made Type O a genre unto themselves.\n\n✦ THE DESIGN\n• Iconic album cover artwork — instantly recognizable\n• Deep, atmospheric color palette\n• A tribute to gothic doom's greatest legacy\n\n✦ FABRIC & FIT\n• Premium quality unisex tee\n• Comfortable, breathable fabric\n• Classic fit — true to size\n• Durable print that won't crack or fade\n\n✦ PERFECT FOR\n→ Gothic metal devotees and doom fans\n→ Concert nights, vinyl sessions, and midnight walks\n→ A meaningful gift for fans of dark, romantic metal\n\n✦ STYLE TIP: Layer under a black cardigan or leather jacket for the ultimate goth look.\n\n🖤 Deathlipse — where romance meets the void.",
        "tags": ["type o negative tee", "gothic metal shirt", "doom metal tshirt", "dark romantic tee", "album art shirt", "goth band merch", "concert shirt", "metalhead gift", "green gothic tee", "90s metal band", "alternative tshirt", "dark music merch", "unisex band tee"]
    },
    # 17) Type O Negative Pillow
    {
        "id": 1861647439,
        "title": "Type O Negative Pillow | Gothic Metal Home Decor | Dark Art Throw Cushion | Metalhead Bedroom Gift | Goth Room Accent",
        "description": "Bring gothic doom into your living space with this Type O Negative-inspired throw pillow — because even your decor should be heavy.\n\nThis isn't just a pillow — it's a portal to the world of gothic metal, right there on your couch. The design channels the dark, romantic energy of Type O's iconic aesthetic, making it the perfect accent piece for any metalhead's sanctuary.\n\n✦ DESIGN\n• Type O Negative-inspired gothic artwork\n• Rich, moody color palette\n• High-resolution print on premium fabric\n\n✦ PILLOW DETAILS\n• Spun polyester cover — soft and durable\n• Hidden zipper for easy cover removal\n• Machine washable for easy care\n• Available in standard throw pillow size\n\n✦ STYLE YOUR DARK SPACE\n→ Bedroom accent for goth and metal aesthetics\n→ Living room conversation piece\n→ Dorm room upgrade for the alternative student\n→ Gift for the metalhead who's decorated everything else\n\n🖤 Deathlipse — dark art, from head to home.",
        "tags": ["type o negative pillow", "gothic home decor", "metal throw pillow", "dark art cushion", "goth room decor", "metalhead gift", "band merch home", "doom metal decor", "y2k goth pillow", "alternative decor", "dark bedroom", "music fan gift", "gothic accent"]
    },
    # 18) Metal Wedding Invitations
    {
        "id": 1890231678,
        "title": "Gothic Wedding Invitation Set | Black Rose Metal Theme Postcard | Dark Romance Customizable Cards | Alternative Wedding Stationery",
        "description": "Say 'I do' the dark way — these gothic wedding invitations prove that true love is beautifully brutal.\n\nFor couples who met in the mosh pit, bonded over blast beats, or simply refuse to have a basic wedding — these black rose metal-themed invitation postcards are your perfect match. Customizable, elegant, and unapologetically dark.\n\n✦ THE DESIGN\n• Black rose motif with gothic metalwork borders\n• Dark, romantic aesthetic — elegant yet rebellious\n• Fully customizable text — your names, date, venue, details\n\n✦ WHAT'S INCLUDED\n• Premium postcard-style invitations\n• Envelopes included with each set\n• Multiple bundle sizes available\n• High-quality print on thick cardstock\n\n✦ PERFECT FOR\n→ Gothic / alternative / metal-themed weddings\n→ Halloween weddings and dark romance celebrations\n→ Couples who want their stationery to match their playlist\n→ Engagement parties and save-the-dates\n\n✦ HOW TO ORDER: Select your bundle size and share your custom details in the personalization box.\n\n🖤 Deathlipse — for the couple that headbangs together.",
        "tags": ["gothic wedding", "metal wedding cards", "black rose invite", "dark wedding set", "alternative wedding", "gothic invitation", "customizable cards", "halloween wedding", "dark romance decor", "goth couple gift", "heavy metal wedding", "unique wedding", "postcard invite set"]
    },
    # 19) Suicide Silence Metal Band Hoodie
    {
        "id": 1846782730,
        "title": "Suicide Silence Inspired Hoodie | Deathcore Band Sweatshirt | Extreme Metal Pullover | Heavy Metal Gift | Dark Art Hoodie",
        "description": "Descend into the abyss with this Suicide Silence-inspired hoodie — deathcore darkness, wearable form.\n\nCapturing the suffocating heaviness and raw brutality of one of deathcore's founding acts, this hoodie is built for those who live in the breakdown. The bold graphic channels the band's relentless energy, making it a staple for extreme metal warriors.\n\n✦ THE DESIGN\n• Brutal deathcore-inspired illustration\n• Bold, high-impact graphic print\n• Captures the intensity of extreme metal\n\n✦ HOODIE SPECS\n• 50% cotton / 50% polyester heavy blend\n• Spacious kangaroo pocket\n• Adjustable drawstring hood\n• Durable construction for pit-tested wear\n• Ethically manufactured\n\n✦ FOR THE\n→ Deathcore faithful and extreme metal warriors\n→ Concert-goers who need pit-ready attire\n→ Anyone who believes there's no such thing as too heavy\n\n🖤 Deathlipse — the sound of darkness, the look of fury.",
        "tags": ["suicide silence hoodie", "deathcore merch", "extreme metal hoodie", "heavy metal band", "brutal metal hoodie", "dark art pullover", "metalhead gift", "concert hoodie", "death metal merch", "underground metal", "band sweatshirt", "gothic hoodie", "alternative fashion"]
    },
    # 20) Megadeth Dystopia T-Shirt
    {
        "id": 1703481502,
        "title": "Megadeth Dystopia T-Shirt | Thrash Metal Band Tee | Vintage Concert Graphic | Heavy Metal Gift | Unisex Black Band Shirt",
        "description": "Suit up for the apocalypse with this Megadeth Dystopia tee — thrash metal royalty, printed to perfection.\n\nThis black tee wears like a chapter in a tour memoir — faded edges, stark lettering, a hard-edge print that still moves with your body. The Dystopia graphic captures the politically charged, technically devastating sound that has made Megadeth thrash metal's enduring force.\n\n✦ THE DESIGN\n• Megadeth Dystopia album-inspired graphic\n• Stark, powerful lettering with vintage tour aesthetic\n• A wearable piece of thrash metal history\n\n✦ QUALITY\n• Premium unisex tee — soft, breathable, durable\n• Fade-resistant print technology\n• Classic fit — true to size\n• Pre-shrunk for consistent wash-to-wash sizing\n\n✦ WHO NEEDS THIS\n→ Megadeth fans and thrash metal loyalists\n→ Vintage band tee collectors\n→ Concert-goers and festival warriors\n→ Anyone gifting a metalhead\n\n🖤 Deathlipse — peace sells, but we're not buying.",
        "tags": ["megadeth tshirt", "dystopia band tee", "thrash metal shirt", "vintage concert tee", "heavy metal gift", "black band shirt", "metal music merch", "guitarist shirt", "rock band tee", "metalhead tshirt", "80s metal band", "unisex band tee", "festival tee"]
    },
    # 21) Megadeth Heavy Metal T-Shirt
    {
        "id": 1703506726,
        "title": "Megadeth Thrash Metal T-Shirt | 80s Heavy Metal Band Tee | Skull Art Graphic Shirt | Metalhead Gift | Punk Rock Fashion",
        "description": "Channel four decades of thrash fury with this Megadeth-inspired heavy metal tee — iconic, aggressive, timeless.\n\nInspired by the legendary artwork that defined an entire genre, this t-shirt brings the explosive energy of 80s thrash metal into your everyday wardrobe. The graphic captures the dark, skull-laden aesthetic that has made Megadeth's imagery as unforgettable as their riffs.\n\n✦ DESIGN\n• Skull-centric artwork inspired by classic thrash metal\n• Bold, aggressive graphic that commands attention\n• A tribute to the golden age of 80s metal\n\n✦ SPECS\n• Premium cotton-poly blend\n• Unisex relaxed fit — true to size\n• High-quality, fade-resistant print\n• Pre-shrunk and comfortable from day one\n\n✦ PERFECT FOR\n→ Thrash metal fans and vinyl collectors\n→ 80s nostalgia nights and retro concert vibes\n→ A timeless gift for any metalhead\n\n🖤 Deathlipse — thrashing since day one.",
        "tags": ["megadeth shirt", "thrash metal tee", "80s metal band", "skull art tshirt", "heavy metal fashion", "punk rock shirt", "metalhead gift", "dark art tee", "grunge fashion", "rock band merch", "vintage metal tee", "alternative rock", "concert tshirt"]
    },
    # 22) Mystical Jesus Dark Forest Hoodie
    {
        "id": 1680197899,
        "title": "Dark Forest Jesus Hoodie | Moonlight Spiritual Sweatshirt | Gothic Christian Art | Mystical Religious Pullover | Unique Gift",
        "description": "Where faith meets the forest floor — this mystical Jesus hoodie is spiritual art wrapped in gothic darkness.\n\nSet against the backdrop of a dark forest illuminated by shimmering moonlight, the figure of Jesus creates a striking contrast between the sacred and the shadowy. This design speaks to those who find spirituality in the mysterious, the quiet, the beautifully dark corners of faith.\n\n✦ THE ARTWORK\n• Jesus figure in a moonlit dark forest setting\n• Contrast between divine light and forest shadow\n• A contemplative, conversation-starting design\n\n✦ HOODIE QUALITY\n• Premium cotton-polyester blend\n• Soft, warm interior for maximum comfort\n• Adjustable drawstring hood\n• Spacious kangaroo pocket\n• Unisex fit — see size chart\n\n✦ FOR THOSE WHO\n→ Find beauty where light meets shadow\n→ Appreciate spiritual art with a dark edge\n→ Want a hoodie that sparks deeper conversations\n→ Love unique, statement-making fashion\n\n🖤 Deathlipse — where the sacred meets the shadows.",
        "tags": ["dark forest hoodie", "jesus moonlight art", "gothic christian", "spiritual hoodie", "mystical sweatshirt", "religious art hoodie", "unique faith gift", "dark aesthetic", "contemplative art", "moonlit forest", "symbolic clothing", "unisex statement", "artistic pullover"]
    },
    # 23) Opeth Full Zip Hoodie
    {
        "id": 1839624983,
        "title": "Opeth Full Zip Hoodie | Progressive Metal Band Jacket | Gothic Rock Sweatshirt | Dark Art Metalhead Gift | Unisex Zip Up",
        "description": "Zip into the darkness with this Opeth-inspired full zip hoodie — progressive metal's finest, now in jacket form.\n\nUnlike a pullover, this full-zip design gives you layering freedom while showcasing the haunting Opeth-inspired artwork front and center. Perfect for throwing on over a band tee before a show or as your daily armor against the ordinary.\n\n✦ DESIGN\n• Opeth-inspired gothic metal illustration\n• Full front graphic with complementary back detail\n• Premium print quality — vivid and fade-resistant\n\n✦ HOODIE FEATURES\n• Full-length YKK-quality zipper\n• Two side pockets for warmth and convenience\n• Adjustable drawstring hood\n• Premium cotton-poly blend for softness and durability\n• Unisex fit — see our size chart\n\n✦ VERSATILE STYLING\n→ Layer over any band tee for instant cool\n→ Lightweight enough for indoor venues\n→ Warm enough for outdoor festivals\n→ The perfect transitional season jacket\n\n🖤 Deathlipse — zip up, tune out, turn it up.",
        "tags": ["opeth zip hoodie", "progressive metal", "full zip hoodie", "metal band jacket", "gothic sweatshirt", "dark art zip up", "metalhead gift", "unisex band hoodie", "concert jacket", "death metal merch", "rock zip hoodie", "alternative fashion", "music lover gift"]
    },
    # 24) Motorhead Horror Crime Stories Hoodie
    {
        "id": 1829524802,
        "title": "Motorhead Inspired Horror Hoodie | British Rock Band Pullover | Punk Metal Sweatshirt | Gothic Dark Art | Metalhead Gift",
        "description": "Crank it to eleven with this Motörhead-inspired horror hoodie — a tribute to the band that invented the speed of darkness.\n\nThe graphic tells a tale straight from the underground — horror crime imagery intertwined with the raw, unfiltered aesthetic of British punk-metal. It's for the fans who know that clean living is for the weak, and that the only volume setting is LOUDER.\n\n✦ THE ARTWORK\n• Horror crime comic-inspired illustration\n• Captures the raw, unpolished spirit of British rock\n• Dark art that tells a story\n\n✦ BUILD QUALITY\n• 50% cotton / 50% polyester heavy blend\n• Kangaroo pocket and adjustable drawstring hood\n• One-piece body — no side seams\n• Ethically sourced, OEKO-TEX certified\n\n✦ BORN TO WEAR\n→ Motörhead faithful and punk-metal crossover fans\n→ British rock enthusiasts\n→ Anyone who believes sleep is for the weak\n\n🖤 Deathlipse — born to lose, live to win.",
        "tags": ["motorhead hoodie", "british rock band", "punk metal hoodie", "horror art hoodie", "gothic dark art", "metalhead gift", "80s metal merch", "rock band pullover", "goth punk hoodie", "alternative hoodie", "heavy metal fashion", "dark culture wear", "concert sweatshirt"]
    },
    # Remaining listings - I'll add more
    # 25) Opeth Progressive Metal T-Shirt (Peacock)
    {
        "id": 1699215311,
        "title": "Opeth Peacock Skull T-Shirt | Progressive Metal Art Tee | Gothic Fantasy Graphic | Death Metal Gift | Dark Art Unisex Shirt",
        "description": "Where beauty decays and skulls bloom — this Opeth-inspired peacock tee is progressive metal's most haunting visual.\n\nA majestic peacock stands sentinel over a pile of skulls and bones, capturing the duality that defines Opeth's music — beauty and brutality, life and death, light and shadow. This intricate design is a wearable masterpiece for fans who understand that the heaviest art is also the most beautiful.\n\n✦ DESIGN\n• Peacock and skull artwork — the Sorceress era reimagined\n• Intricate detail and rich color work\n• A piece of dark fantasy art on premium cotton\n\n✦ FIT & QUALITY\n• Premium unisex tee — soft and breathable\n• Fade-resistant print technology\n• True to size — see our chart\n• Pre-shrunk for consistent fit\n\n✦ FOR THE FAN WHO\n→ Appreciates art as complex as the music\n→ Wants progressive metal imagery beyond the obvious\n→ Needs a gift-worthy tee for a discerning metalhead\n\n🖤 Deathlipse — where the beautiful and the brutal collide.",
        "tags": ["opeth tshirt", "peacock skull tee", "progressive metal", "gothic fantasy art", "death metal shirt", "dark art tee", "metalhead gift", "occult fashion", "morbid art shirt", "heavy metal tee", "90s metal band", "band merch tee", "alternative shirt"]
    },
    # 26) Nirvana Grunge Tote Bag
    {
        "id": 4361050810,
        "title": "Nirvana Grunge Canvas Tote Bag | 90s Band Logo Carryall | Vintage Rock Music Gift | Eco Friendly Shopping Bag | Festival Accessory",
        "description": "Carry your essentials with a grunge edge — this Nirvana-inspired tote bag is 90s rebellion you can sling over your shoulder.\n\nThe faded, worn-in Nirvana grunge artwork sits on heavy, tightly woven cotton that feels built for years of daily abuse. Whether you're hauling records, groceries, or festival essentials, this tote is as versatile as it is iconic.\n\n✦ DESIGN\n• Vintage Nirvana grunge aesthetic — faded, rebellious, authentic\n• Heavy cotton canvas for durability\n• Spacious enough for vinyl records, books, and everyday carry\n\n✦ TOTE SPECS\n• Thick, tightly woven canvas\n• Reinforced stitching on handles and seams\n• Generous interior — no cramming required\n• Eco-friendly alternative to plastic bags\n\n✦ USE IT FOR\n→ Record store runs and bookshop browsing\n→ Festival essentials — sunscreen, merch, snacks\n→ Everyday groceries with attitude\n→ A thoughtful gift for 90s grunge fans\n\n🖤 Deathlipse — even your bags have good taste in music.",
        "tags": ["nirvana tote bag", "grunge canvas bag", "90s band merch", "vintage rock tote", "music fan gift", "eco friendly bag", "festival tote", "alternative style", "concert carryall", "rock band bag", "everyday canvas bag", "grunge aesthetic", "slouchy tote bag"]
    },
    # 27) Gojira Inspired Metallic Circle Design Hoodie
    {
        "id": 4385200967,
        "title": "Gojira Inspired Hoodie | Metallic Circle Art Pullover | Eco Metal Band Sweatshirt | French Death Metal Gift | Unisex Hoodie",
        "description": "Forged in fire, inspired by the cosmos — this Gojira-inspired hoodie is for those who headbang and recycle.\n\nFeaturing a bold, metallic-circle emblem that feels like a relic from a sci-fi concert poster, this hoodie channels the cosmic heaviness and environmental consciousness of French death metal's greatest export. Heavy, magnetic, and alive with energy.\n\n✦ THE DESIGN\n• Metallic circle Gojira-inspired emblem\n• Sci-fi meets heavy metal aesthetic\n• Bold graphic that commands the room\n\n✦ BUILT RIGHT\n• 50% cotton / 50% polyester heavy blend\n• Spacious kangaroo pocket\n• Adjustable drawstring hood\n• Ethically made with US-grown cotton\n• OEKO-TEX certified — because Gojira fans care about the planet\n\n✦ FOR THOSE WHO\n→ Live by the riff and respect the planet\n→ Need concert-grade comfort for daily wear\n→ Want to gift a Gojira fan something they'll actually wear\n\n🖤 Deathlipse — heavy on sound, light on the planet.",
        "tags": ["gojira hoodie", "metallic circle art", "eco metal hoodie", "french metal band", "death metal merch", "rock fan sweatshirt", "metalhead gift", "alternative fashion", "concert hoodie", "heavy metal pullover", "music lover hoodie", "festival hoodie", "unisex band hoodie"]
    },
]

def update_listing(listing_id, title, description, tags):
    url = f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}"
    
    data = {
        "title": title,
        "description": description,
    }
    
    # Tags need to be sent as repeated params
    for i, tag in enumerate(tags[:13]):
        data[f"tags[{i}]"] = tag
    
    resp = requests.patch(url, headers=HEADERS, data=data)
    return resp.status_code, resp.text

def main():
    total = len(OPTIMIZED)
    success = 0
    failed = 0
    
    print(f"{'='*60}")
    print(f"ETSY LISTING OPTIMIZER - Deathlipse Shop")
    print(f"Optimizing {total} listings...")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(OPTIMIZED):
        lid = item["id"]
        title = item["title"]
        desc = item["description"]
        tags = item["tags"]
        
        print(f"[{i+1}/{total}] Updating: {title[:60]}...")
        
        status, response = update_listing(lid, title, desc, tags)
        
        if status == 200:
            print(f"  ✅ SUCCESS (HTTP {status})")
            success += 1
        else:
            print(f"  ❌ FAILED (HTTP {status}): {response[:200]}")
            failed += 1
        
        # Rate limit - Etsy allows ~10 requests/second
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"OPTIMIZATION COMPLETE!")
    print(f"✅ Success: {success}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
