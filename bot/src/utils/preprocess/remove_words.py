import langdetect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bot.src.utils.preprocess.tokenizer import handle as tokenizer
from bot.src.utils.proxies import logger
nltk.download('stopwords')
nltk.download('punkt')

languages_map={"ar": "arabic","bg": "bulgarian","ca": "catalan","cz": "czech","da": "danish","nl": "dutch","en": "english","fi": "finnish","fr": "french","de": "german","hi": "hindi","hu": "hungarian","id": "indonesian","it": "italian","nb": "norwegian","pl": "polish","pt": "portuguese","ro": "romanian","ru": "russian","sk": "slovak","es": "spanish","sv": "swedish","tr": "turkish","uk": "ukrainian","vi": "vietnamese"}

async def deteccion(texto):
    try:
        if isinstance(texto, list):
            return await procesar_lista_multilingue(texto)
        elif isinstance(texto, str):
            texto, _ = await procesar_texto_normal(texto)
            return texto
    except Exception as e:
        logger.error("Detección no detectó instancia, detectó", {e})

async def procesar_lista_multilingue(lista):
    resultados = []
    idioma=None
    for item in lista:
        if isinstance(item, dict):
            new_item = {}
            for key, value in item.items():
                try:
                    if key in ["user", "bot", "search", "url", "documento"]:
                        if not idioma:
                            new_item[key], idioma = await procesar_texto_normal(value)
                        else:
                            new_item[key] = await procesar_texto_normal(value, idioma, lock=True)
                    else:
                        new_item[key] = value  
                except KeyError:
                    # Manejo de error por valor inexistente
                    continue
            resultados.append(new_item)
    return resultados
async def procesar_texto_normal(texto, idioma=None, lock=None):
    textofiltrr=None
    if texto:
        if idioma:
            pass
        else:
            idioma = langdetect.detect_langs(texto)[0].lang
        textofiltrr = await filtrar_palabras_irrelevantes(texto, idioma)
    if textofiltrr:
        if lock:
            return "".join(textofiltrr)
        else:
            return "".join(textofiltrr), idioma
    else:
        logger.error("No se detectó ningún idioma en el texto.")


cached_stopwords = {}

async def filtrar_palabras_irrelevantes(texto, idioma):
    if idioma in cached_stopwords:
        palabras_irrelevantes = cached_stopwords[idioma]
    elif languages_map.get(idioma) in stopwords.fileids():
        palabras_irrelevantes = set(stopwords.words(languages_map[idioma]))
        cached_stopwords[idioma] = palabras_irrelevantes
    else:
        return texto

    palabras = word_tokenize(texto)
    palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in palabras_irrelevantes]

    return " ".join(palabras_filtradas)

async def handle(texto, max_tokens):
    resultado = await deteccion(texto)
    tokens, tokencount = await tokenizer(input_data=resultado, max_tokens=max_tokens)
    return tokens, tokencount