import langdetect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from bot.src.utils.preprocess.tokenizer import handle as tokenizer
from bot.src.utils.proxies import logger
nltk.download('stopwords')
nltk.download('punkt')

languages_map={"ar": "arabic","bg": "bulgarian","ca": "catalan","cz": "czech","da": "danish","nl": "dutch","en": "english","fi": "finnish","fr": "french","de": "german","hi": "hindi","hu": "hungarian","id": "indonesian","it": "italian","nb": "norwegian","pl": "polish","pt": "portuguese","ro": "romanian","ru": "russian","sk": "slovak","es": "spanish","sv": "swedish","tr": "turkish","uk": "ukrainian","vi": "vietnamese"}

async def deteccion(texto):
    if isinstance(texto, list):
        return await procesar_lista_multilingue(texto)
    else:
        return await procesar_texto_normal(texto)

async def procesar_lista_multilingue(lista):
    resultados = []
    for item in lista:
        if isinstance(item, dict):
            new_item = {}
            for key, value in item.items():
                try:
                    if key in ["user", "bot", "search", "url", "documento"]:
                        new_item[key] = await procesar_texto_normal(value)
                    else:
                        new_item[key] = value
                except KeyError:
                    # Manejo de error por valor inexistente
                    continue
            resultados.append(new_item)
    return resultados
async def procesar_texto_normal(texto):
    # Divide el texto en oraciones con información del idioma
    oraciones_por_idioma = await dividir_texto_por_idioma(texto)
    # Filtra las palabras irrelevantes en cada oración y guarda la oración filtrada
    for oracion_info in oraciones_por_idioma:
        idioma = oracion_info["idioma"]
        oracion = oracion_info["oracion"]
        oracion_filtrada = await filtrar_palabras_irrelevantes(oracion, idioma)
        oracion_info["oracion_filtrada"] = oracion_filtrada

    if oraciones_por_idioma:
        texto_filtrado = " ".join([oracion_info["oracion_filtrada"] for oracion_info in oraciones_por_idioma])
        return texto_filtrado
    else:
        logger.error("No se detectó ningún idioma en el texto.")

async def dividir_texto_por_idioma(texto):
    oraciones_con_idioma = []
    # Separa el texto en oraciones
    oraciones = sent_tokenize(texto)
    # Para cada oración, detecta el idioma
    for oracion in oraciones:
        if oracion.strip():
            try:
                idioma_detectado = langdetect.detect_langs(oracion)[0].lang
                oraciones_con_idioma.append({"idioma": idioma_detectado, "oracion": oracion})
            except langdetect.lang_detect_exception.LangDetectException:
                continue

        else: logger.error("no se detectó oracion")
    return oraciones_con_idioma

async def filtrar_palabras_irrelevantes(texto, idioma):
    # Comprueba si hay palabras irrelevantes disponibles para el idioma específico
    if languages_map.get(idioma) in stopwords.fileids():
        palabras_irrelevantes = stopwords.words()
    else:
        # Si no hay palabras irrelevantes disponibles, devuelve el texto sin cambios
        return texto

    palabras = word_tokenize(texto)
    palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in palabras_irrelevantes]

    return " ".join(palabras_filtradas)

async def handle(texto, max_tokens):
    resultado = await deteccion(texto)
    tokens, tokencount = await tokenizer(resultado, max_tokens)
    return tokens, tokencount