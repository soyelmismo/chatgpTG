#from .imaginepy import AsyncImagine, Style, Ratio, Model
import uuid
import io
import secrets
from enum import Enum

AsyncImagine, Styles, Ratio, Model = None, None, None, None
async def main(self, prompt, style, ratio, model, seed=None, negative=None, endpoint=None):
    imagine = AsyncImagine(api=endpoint, proxies=self.proxies)
    try:
        if seed == None:
            seed = secrets.randbelow(10**16)

        img_data = await imagine.sdprem(
            prompt=prompt,
            model=Model.__members__[model],
            style=Styles.__members__[style],
            ratio=Ratio.__members__[ratio],
            negative=negative,
            seed=seed,
            cfg=15,
            high_result = 1,
            priority = 1,
            steps = 50
        )
        await imagine.close()
    except Exception as e:
        raise BufferError(f"error imagine.py: {e}")

    try:    
        imagine = AsyncImagine()
        img_data = await imagine.upscale(image=img_data)

        await imagine.close()

        if img_data == None:
            raise FileNotFoundError("no files")

    except Exception as e:
        raise BufferError(f"error imagine.py: {e}")

    img_io = io.BytesIO(img_data)
    img_io.name = f"{uuid.uuid4()}.png"
    return img_io, seed

# KEY = (style_id, style_name, style_thumb, init_prompt)
class Style(Enum):
    NO_STYLE = (27, 'No style', '', '')
    V3 = (28, 'V3', 'assets/styles_v4/thumb-74.webp', ', 4k, high quality, hdr')
    EUPHORIC = (28, 'Euphoric', 'assets/styles_v4/thumb-20.webp',
                'digital illustration, style of charlie bowater, dreamy colorful cyberpunk colors, euphoric fantasy, epic dreamlike fantasy landscape, beautiful oil matte painting, 8k fantasy art, fantasy art landscape, jessica rossier color scheme, dreamlike diffusion')
    FANTASY = (28, 'Fantasy', 'assets/styles_v4/thumb-25.webp',
               'fantasy matte painting,  fantasy landscape, ( ( thomas kinkade ) ), whimsical, dreamy, alice in wonderland, daydreaming, epic scene, high exposure, highly detailed, tim white, michael whelan')
    CYBERPUNK = (28, 'Cyberpunk', 'assets/styles_v1/thumb_41.webp',
                 ', synthwave image, (neotokyo), dreamy colorful cyberpunk colors, cyberpunk blade runner art, retrofuturism, cyberpunk, beautiful cyberpunk style, cgsociety 9')
    STUDIO_GHIBLI = (28, 'Studio Ghibli', 'assets/styles_v4/thumb-07.webp',
                     'studio ghibli movie still, ghibli screenshot, joe hisaishi, makoto shinkai, cinematic studio ghibli still, fantasy art landscape, whimsical, dreamlike, anime beautiful peace scene, studio ghibli painting, cinematic')
    DISNEY = (28, 'Disney', 'assets/styles_v4/thumb-04.webp',
              'disney animation, disney splash art, disney color palette, disney renaissance film, disney pixar movie still, disney art style, disney concept art :: nixri, wonderful compositions, pixar, disney concept artists, 2d character design')
    GTA = (28, 'GTA', 'assets/styles_v4/thumb-06.webp',
           'gta iv art style, gta art,  gta loading screen art, gta chinatowon art style, gta 5 loading screen poster, grand theft auto 5, grand theft auto video game')
    KAWAII_CHIBI = (28, 'Kawaii Chibi', 'assets/styles_v4/thumb-40.webp',
                    'kawaii chibi romance, fantasy, illustration, Colorful idyllic cheerful, Kawaii Chibi inspired')
    ANIME_V2 = (28, 'Anime V2', 'assets/styles_v1/thumb_37.webp', ', anime atmospheric, atmospheric anime, anime character; full body art, digital anime art, beautiful anime art style, anime picture, anime arts, beautiful anime style, digital advanced anime art, anime painting, anime artwork, beautiful anime art, detailed digital anime art, anime epic artwork')
    ABSTRACT_VIBRANT = (28, 'Abstract Vibrant', 'assets/styles_v4/thumb-31.webp',
                        'vibrant, editorial, abstract elements, colorful, color splatter, realism, Inspired by the style of Ryan Hewett, dynamic realism, soft lighting and intricate details')
    VIBRANT = (27, 'Vibrant', 'assets/styles_v4/thumb-62.webp',
               ', Psychedelic, water colors spots, vibrant color scheme, highly detailed, romanticism style, cinematic, artstation, greg rutkowski')
    PSYCHEDELIC = (28, 'Psychedelic', 'assets/styles_v4/thumb-11.webp',
                   'psychedelic painting, psychedelic dripping colors, colorful detailed projections, android jones and chris dyer, psychedelic vibrant colors, intricate psychedelic patterns, psychedelic visuals, hallucinatory art')
    EXTRA_TERRESTRIAL = (28, 'Extra-terrestrial', 'assets/styles_v4/thumb-26.webp',
                         'deepdream cosmic, painting by android jones, cosmic entity, humanoid creature, james jean soft light 4 k, sci fi, extra terrestrial, cinematic')
    COSMIC = (28, 'Cosmic', 'assets/styles_v4/thumb-01.webp',
              'in cosmic atmosphere, humanitys cosmic future,  space art concept, space landscape, scene in space, cosmic space, beautiful space star planet, background in space, realistic, cinematic, breathtaking view')
    MACRO_PHOTOGRAPHY = (28, 'Macro Photography', 'assets/styles_v4/thumb-05.webp',
                         'macro photography, award winning macro photography, depth of field, extreme closeup, 8k hd, focused')
    PRODUCT_PHOTOGRAPHY = (28, 'Product Photography', 'assets/styles_v4/thumb-10.webp',
                           'product photo studio lighting,  high detail product photo, product photography, commercial product photography, realistic, light, 8k, award winning product photography, professional closeup')
    POLAROID = (27, 'Polaroid', 'assets/styles_v4/thumb-54.webp',
                ', old polaroid, 35mm')
    NEO_FAUVISM = (28, 'Neo fauvism', 'assets/styles_v4/thumb-28.webp',
                   'neo-fauvism painting, neo-fauvism movement, digital illustration, poster art, cgsociety saturated colors, fauvist')
    POP_ART = (28, 'Pop Art', 'assets/styles_v4/thumb-23.webp',
               'pop art painting, detailed patterns pop art, silkscreen pop art, pop art poster, roy lichtenstein style')
    POP_ART_II = (28, 'Pop Art II', 'assets/styles_v4/thumb-70.webp',
                  'style of shepherd fairey, (Andy Warhol art style), silkscreen pop art, martin ansin artwork, high contrast illustrations, lowbrow pop art style, trending on artstatioin, vector style')
    GRAFFITI = (28, 'Graffiti', 'assets/styles_v4/thumb-13.webp',
                'graffiti background, colorful graffiti, graffiti art style, colorful mural, ravi supa, symbolic mural, juxtapoz, pablo picasso, street art')
    SURREALISM = (28, 'Surrealism', 'assets/styles_v4/thumb-12.webp',
                  'salvador dali painting, highly detailed surrealist art, surrealist conceptual art,  masterpiece surrealism, surreal architecture, surrealistic digital artwork, whimsical surrealism, bizarre art')
    BAUHAUS = (28, 'Bauhaus', 'assets/styles_v4/thumb-34.webp',
               'Bauhaus art movement,  by Wassily Kandinsky, bauhaus style painting, geometric abstraction, vibrant colors, painting')
    CUBISM = (28, 'Cubism', 'assets/styles_v4/thumb-33.webp',
              'cubist picasso, cubism,  a cubist painting, heavy cubism, cubist painting, by Carlo Carrà, style of picasso, modern cubism, futuristic cubism')
    JAPANESE_ART = (27, 'Japanese Art', 'assets/styles_v4/thumb-51.webp',
                    ', Ukiyoe, illustration, muted colors')
    SKETCH = (27, 'Sketch', 'assets/styles_v4/thumb-59.webp',
              ', pencil, hand drawn, sketch, on paper')
    ILLUSTRATION = (28, 'Illustration', 'assets/styles_v1/thumb_31.webp',
                    ', minimalistic vector art, illustrative style, style of ian hubert, style of gilles beloeil, inspired by Hsiao-Ron Cheng, style of jonathan solter, style of alexandre chaudret, by Echo Chernik')
    PAINTING = (28, 'Painting', 'assets/styles_v1/thumb_32.webp',
                ', atmospheric dreamscape painting, by Mac Conner, vibrant gouache painting scenery, vibrant painting, vivid painting, a beautiful painting, dream scenery art, instagram art, psychedelic painting, lofi art, bright art')
    PALETTE_KNIFE = (28, 'Palette Knife', 'assets/styles_v4/thumb-17.webp',
                     'detailed impasto brush strokes,  detail acrylic palette knife, thick impasto technique,  palette knife, vibrant 8k colors')
    INK = (27, 'Ink', 'assets/styles_v4/thumb-50.webp',
           ', Black Ink, Hand drawn, Minimal art, artstation, artgem, monochrome')
    ORIGAMI = (28, 'Origami', 'assets/styles_v4/thumb-22.webp',
               'polygonal art, layered paper art, paper origami, wonderful compositions, folded geometry, paper craft, made from paper')
    STAINED_GLASS = (28, 'Stained Glass', 'assets/styles_v4/thumb-09.webp',
                     'intricate wiccan spectrum, stained glass art, vividly beautiful colors, beautiful stained glass window, colorful image, intricate stained glass triptych, gothic stained glass style, stained glass window!!!')
    STICKER = (28, 'Sticker', 'assets/styles_v1/thumb_35.webp',
               ', sticker, sticker art, symmetrical sticker design, sticker - art, sticker illustration, die - cut sticker')
    CLIP_ART = (28, 'Clip Art', 'assets/styles_v4/thumb-69.webp',
                '(((clip art))), clip art illustration, cartoon character, thin black stroke outline, pastel colors, cute illustration,  vector illustration')
    POSTER_ART = (27, 'Poster Art', 'assets/styles_v4/thumb-56.webp',
                  ', album art, Poster, layout, typography, logo, risography, ghibili, simon stalenhag, insane detail, artstation, 8k')
    PAPERCUT_STYLE = (28, 'PaperCut Style', 'assets/styles_v1/thumb_39.webp',
                      ', layered paper art, paper modeling art, paper craft, paper art, papercraft, paper cutout, paper cut out collage artwork, paper cut art')
    COLORING_BOOK = (28, 'Coloring Book', 'assets/styles_v4/thumb-67.webp',
                     ', line art illustration, lineart behance hd, illustration line art style, line art colouring page, decora inspired illustrations, coloring pages, digital line-art, line art!!, thick line art, coloring book page, clean coloring book page, black ink line art, coloring page, detailed line art')
    PATTERN = (28, 'Pattern', 'assets/styles_v4/thumb-71.webp',
               'seamless pattern, ((repetitive pattern)), pattern design, background image, wallpaper,  colorful, decorated, flat design')
    RENDER = (28, 'Render', 'assets/styles_v1/thumb_36.webp',
              ', isometric, polaroid octane render, 3 d render 1 5 0 mm lens, keyshot product render, rendered, keyshot product render pinterest, 3 d product render, 3 d cgi render, 3d cgi render, ultra wide angle isometric view')
    CINEMATIC_RENDER = (27, 'Cinematic Render', 'assets/styles_v4/thumb-47.webp',
                        ', cinematic, breathtaking colors, close-up, cgscociety, computer rendering, by mike winkelmann, uhd, rendered in cinema4d, surface modeling, 8k, render octane, inspired by beksinski')
    COMIC_BOOK = (28, 'Comic Book', 'assets/styles_v4/thumb-48.webp',
                  ', Comic cover, 1960s marvel comic, comic book illustrations')
    COMIC_V2 = (28, 'Comic V2', 'assets/styles_v1/thumb_34.webp',
                ', comic book, john romita senior, inspired by Alton Tobey, by Alan Davis, arachnophobia, by Alton Tobey, as a panel of a marvel comic, marvel comic')
    LOGO = (28, 'Logo', 'assets/styles_v4/thumb-37.webp',
            'creative logo, unique logo, visual identity, geometric type, graphic design, logotype design, brand identity, vector based, trendy typography, best of behance')
    ICON = (28, 'Icon', 'assets/styles_v1/thumb_43.webp',
            ', single vector graphics icon, ios icon, smooth shape, vector')
    GLASS_ART = (28, 'Glass Art', 'assets/styles_v1/thumb_46.webp',
                 ' inside glass ball, translucent sphere, cgsociety 9, glass orb, behance, polished, beautiful digital artwork, exquisite digital art, in a short round glass vase, octane render')
    KNOLLING_CASE = (28, 'Knolling Case', 'assets/styles_v1/thumb_45.webp',
                     ', in  square glass case,  glass cube, glowing, knolling case, ash thorp, studio background,  desktopography, cgsociety 9,  cgsociety, mind-bending digital art')
    SCATTER = (28, 'Scatter', 'assets/styles_v1/thumb_42.webp',
               ', breaking pieces, exploding pieces, shattering pieces,  disintegration, contemporary digital art, inspired by Dan Hillier, inspired by Igor Morski, dramatic digital art, behance art, cgsociety 9, 3d advanced digital art, mind-bending digital art, disintegrating')
    POLY_ART = (27, 'Poly Art', 'assets/styles_v4/thumb-55.webp',
                ', low poly, artstation, studio lightning, stainless steel, grey color scheme')
    CLAYMATION = (28, 'Claymation', 'assets/styles_v4/thumb-19.webp',
                  'clay animation, as a claymation character, claymation style, animation key shot, plasticine, clay animation, stopmotion animation, aardman character design, plasticine models')
    WOOLITIZE = (28, 'Woolitize', 'assets/styles_v4/thumb-27.webp',
                 'cute! c4d, made out of wool, volumetric wool felting, wool felting art, houdini sidefx, rendered in arnold, soft smooth lighting, soft pastel colors')
    MARBLE = (28, 'Marble', 'assets/styles_v4/thumb-02.webp',
              'in greek marble style, classical antiquities, ancient greek classical ancient greek art, marble art, realistic, cinematic')
    VAN_GOGH = (27, 'Van Gogh', 'assets/styles_v4/thumb-61.webp',
                ', painting, by van gogh')
    SALVADOR_DALI = (27, 'Salvador Dali', 'assets/styles_v4/thumb-58.webp',
                     ', Painting, by salvador dali, allegory, surrealism, religious art, genre painting, portrait, painter, still life')
    PICASSO = (27, 'Picasso', 'assets/styles_v4/thumb-53.webp',
               ', painting, by pablo picaso, cubism')
    ARCHITECTURE = (28, 'Architecture', 'assets/styles_v1/thumb_47.webp',
                    ', modern architecture design, luxury architecture, bright, very beautiful, trending on unsplash, breath taking')
    INTERIOR = (28, 'Interior', 'assets/styles_v1/thumb_40.webp',
                ', modern architecture by makoto shinkai, ilya kuvshinov, lois van baarle, rossdraws and frank lloyd wright')
    ABSTRACT_CITYSCAPE = (28, 'Abstract Cityscape', 'assets/styles_v4/thumb-46.webp',
                          'abstract cityscape, Ultra Realistic Cinematic Light abstract, futuristic, cityscape, Out of focus background and incredible 16k resolution produced in Unreal Engine 5 and Octan render')
    DYSTOPIAN = (28, 'Dystopian', 'assets/styles_v4/thumb-08.webp',
                 'cifi world, cybernetic civilizations, peter gric and dan mumford,   brutalist dark futuristic, dystopian brutalist atmosphere, dark dystopian world, cinematic 8k, end of the world, doomsday')
    FUTURISTIC = (27, 'Futuristic', 'assets/styles_v4/thumb-49.webp',
                  ', futuristic, elegant atmosphere, glowing lights, highly detailed, digital painting, artstation, concept art, smooth sharp focus, illustration, mars ravelo, gereg rutkowski')
    NEON = (28, 'Neon', 'assets/styles_v4/thumb-32.webp',
            'neon art style, night time dark with neon colors, blue neon lighting, violet and aqua neon lights, blacklight neon colors, rococo cyber neon lighting')
    CHROMATIC = (28, 'Chromatic', 'assets/styles_v4/thumb-68.webp',
                 '(((chromatic))) vaporwave nostalgia, vaporwave artwork, ((synthwave)), chromatic colors, , 3d render, vibrant chromatic colors, glowing chromatic colors')
    MYSTICAL = (27, 'Mystical', 'assets/styles_v4/thumb-52.webp',
                ', fireflies, deep focus, d&d, fantasy, intricate, elegant, highly detailed, digital painting, artstation, concept art, matte, sharp focus, illustration, hearthstrom, gereg rutkowski, alphonse mucha, andreas rocha')
    LANDSCAPE = (28, 'Landscape', 'assets/styles_v1/thumb_44.webp',
                 ', landscape 4k, beautiful landscapes, nature wallpaper, 8k photography')
    RAINBOW = (28, 'Rainbow', 'assets/styles_v4/thumb-15.webp',
               'intricate rainbow environment, rainbow bg, from lorax movie, pixar color palette, volumetric rainbow lighting, gorgeous digital painting, 8k cinematic')
    CANDYLAND = (28, 'Candyland', 'assets/styles_v4/thumb-18.webp',
                 'candy land style,  whimsical fantasy landscape art, japanese pop surrealism, colorfull digital fantasy art, made of candy and lollypops, whimsical and dreamy')
    MINECRAFT = (28, 'Minecraft', 'assets/styles_v4/thumb-03.webp',
                 'minecraft build, style of minecraft, pixel style, 8 bit, epic, cinematic, screenshot from minecraft, detailed natural lighting, minecraft gameplay, mojang,  minecraft mods, minecraft in real life,  blocky like minecraft')
    PIXEL_ART = (28, 'Pixel Art', 'assets/styles_v1/thumb_38.webp',
                 ', one pixel brush, pixelart, colorful pixel art')
    RENNAISANCE = (28, 'Rennaisance', 'assets/styles_v4/thumb-24.webp',
                   'renaissance period, neo-classical painting, italian renaissance workshop, pittura metafisica, raphael high renaissance, ancient roman painting, michelangelo painting, Leonardo da Vinci, italian renaissance architecture')
    ROCOCCO = (28, 'Rococco', 'assets/styles_v4/thumb-35.webp',
               'francois boucher oil painting, rococco style,  rococco lifestyle, a flemish Baroque, by Karel Dujardin, vintage look, cinematic hazy lighting')
    MEDIEVAL = (28, 'Medieval', 'assets/styles_v4/thumb-21.webp',
                'movie still from game of thrones, powerful fantasy epic, middle ages, lush green landscape, olden times, roman empire, 1400 ce, highly detailed background, cinematic lighting, 8k render, high quality, bright colours')
    RETRO = (28, 'Retro', 'assets/styles_v1/thumb_30.webp', ', retro futuristic illustration, featured on illustrationx, art deco illustration, beautiful retro art, stylized digital illustration, highly detailed vector art, ( ( mads berg ) ), automotive design art, epic smooth illustration, by mads berg, stylized illustration, ash thorp khyzyl saleem, clean vector art')
    RETROWAVE = (27, 'Retrowave', 'assets/styles_v4/thumb-57.webp',
                 ', Illustration, retrowave art, noen light, retro, digital art, trending on artstation')
    STEAMPUNK = (27, 'Steampunk', 'assets/styles_v4/thumb-60.webp',
                 ' steampunk, stylized digital illustration, sharp focus, elegant, intricate, digital painting, artstation concept art, global illumination, ray tracing, advanced technology, chaykan howard, campion pascal, cooke darwin, davis jack, pink atmosphere')
    AMAZONIAN = (28, 'Amazonian', 'assets/styles_v4/thumb-29.webp',
                 'amazonian cave, landscape, jungle, waterfall, moss-covered ancient ruins, Dramatic lighting and intense colors, mesmerizing details of the environment and breathtaking atmosphere')
    AVATAR = (28, 'Avatar', 'assets/styles_v4/thumb-16.webp',
              'avatar movie, avatar with blue skin, vfx movie, cinematic lighting, utopian jungle, pandora jungle, sci-fi nether world, lost world, pandora fantasy landscape,lush green landscape, high quality render')
    GOTHIC = (28, 'Gothic', 'assets/styles_v4/thumb-14.webp',
              'goth lifestyle, dark goth, grunge, cinematic photography, dramatic dark scenery, dark ambient beautiful')
    HAUNTED = (28, 'Haunted', 'assets/styles_v4/thumb-36.webp',
               'horror cgi 4 k, scary color art in 4 k, horror movie cinematography, insidious, la llorona, still from animated horror movie, film still from horror movie, haunted, eerie, unsettling, creepy')
    WATERBENDER = (28, 'Waterbender', 'assets/styles_v4/thumb-38.webp',
                   'water elements, fantasy, water, exotic, A majestic composition with water elements, waterfall, lush moss and exotic flowers, highly detailed and realistic, dynamic lighting')
    AQUATIC = (28, 'Aquatic', 'assets/styles_v4/thumb-44.webp',
               'graceful movement with intricate details, inspired by artists like Lotte Reiniger, Carne Griffiths and Alphonse Mucha. Dreamy and surreal atmosphere, twirling in an aquatic landscape with water surface')
    FIREBENDER = (28, 'Firebender', 'assets/styles_v4/thumb-39.webp',
                  'fire elements, fantasy, fire, lava, striking. A majestic composition with fire elements, fire and ashes surrounding, highly detailed and realistic, cinematic lighting')
    FORESTPUNK = (28, 'Forestpunk', 'assets/styles_v4/thumb-41.webp',
                  'forestpunk, vibrant, HDRI, organic motifs and pollen in the air, bold vibrant colors and textures, spectacular sparkling rays, photorealistic quality with Hasselblad')
    VIBRANT_VIKING = (28, 'Vibrant Viking', 'assets/styles_v4/thumb-45.webp',
                      'Viking era, digital painting, pop of colour, forest, paint splatter, flowing colors, Background of lush forest and earthy tones, Artistic representation of movement and atmosphere')
    SAMURAI = (28, 'Samurai', 'assets/styles_v4/thumb-43.webp',
               'samurai lifesyle, miyamoto musashi, Japanese art, ancient japanese samurai, feudal japan art, feudal japan art')
    ELVEN = (28, 'Elven', 'assets/styles_v4/thumb-42.webp',
             'elven lifestyle, photoreal, realistic, 32k quality, crafted by Elves and engraved in copper, elven fantasy land, hyper detailed')
    SHAMROCK_FANTASY = (28, 'Shamrock Fantasy', 'assets/styles_v4/thumb-30.webp',
                        'shamrock fantasy, fantasy, vivid colors, grapevine, celtic fantasy art, lucky clovers, dreamlike atmosphere, captivating details, soft light and vivid colors')
    # Experimental
    EARTHBENDER = (28, "Earthbender", "EXPERIMENTAL",
                   ", earth elements, fantasy, rock, ground, grounding. A robust composition with earth elements, rocks and soil surrounding, highly detailed and realistic, cinematic lighting")
    AIRBENDER = (28, "Airbender", "EXPERIMENTAL",
                 ", air elements, fantasy, wind, clouds, liberating. A tranquil composition with air elements, wind gusts and floating clouds surrounding, highly detailed and realistic, cinematic lighting")
    METALBENDER = (28, "Metalbender", "EXPERIMENTAL",
                   ", metal elements, fantasy, metal, steel, tenacious. A sturdy composition with metal elements, shards and steel surrounding, highly detailed and realistic, cinematic lighting")
    BLOODBENDER = (28, "Bloodbender", "EXPERIMENTAL",
                   ", blood elements, fantasy, blood, body, unsettling. A dark composition with blood elements, veins and body fluid surrounding, highly detailed and realistic, cinematic lighting")
    LIGHTNINGBENDER = (28, "Lightbender", "EXPERIMENTAL",
                       ", lightning elements, fantasy, electricity, thunder, electrifying. A shocking composition with lightning elements, sparks and electricity surrounding, highly detailed and realistic, cinematic lighting")
    SPIRITBENDER = (28, "Spiritbender", "EXPERIMENTAL",
                    ", spirit elements, fantasy, spirit, ethereal, mystifying. A mystical composition with spirit elements, auras and spiritual energy surrounding, highly detailed and realistic, cinematic lighting")
    LAVABENDER = (28, "Lavabender", "EXPERIMENTAL",
                  ", lava elements, fantasy, molten rock, heat, blistering. A fierce composition with lava elements, molten rock and heat waves surrounding, highly detailed and realistic, cinematic lighting")
    WATERHEALER = (28, "Waterbender", "EXPERIMENTAL",
                   ", healing elements, fantasy, water, rejuvenation, restorative. A soothing composition with healing elements, glowing water and soothing vibes surrounding, highly detailed and realistic, cinematic lighting")

image_api_styles = [style.name for style in Style]

class Ratio(Enum):
    R_1X1 = (640, 640, "1:1")
    R_4X3 = (640, 480, "4:3")
    R_3X2 = (640, 320, "3:2")
    R_2X3 = (320, 640, "2:3")
    R_16X9 = (640, 360, "16:9")
    R_9X16 = (360, 640, "9:16")
    R_5X4 = (640, 512, "5:4")
    R_4X5 = (512, 640, "4:5")
    R_3X1 = (640, 192, "3:1")
    R_3X4 = (480, 640, "3:4")