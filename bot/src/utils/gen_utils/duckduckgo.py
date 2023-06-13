from itertools import islice
from duckduckgo_search import DDGS
from bot.src.utils.config import pred_lang
async def search(self=None, prompt=None):
    if not prompt:
        return
    if not self.lang:
        self.lang=pred_lang
    resultados=[]
    with DDGS() as ddgs:
        ddgs_gen = ddgs.text(prompt, backend="api", region=f'{self.lang}-{self.lang}', safesearch='Off', timelimit='y')
        for r in islice(ddgs_gen, 10):
            resultados.append(r)
    formatted_backend = []
    formatted_results = []
    for resultado in resultados:
        title = resultado['title']
        href = resultado['href']
        body = resultado['body']
        formatted_result = f"- [{title}]({href})"
        backend_result = f"[{title}]({href}): {body}"
        formatted_results.append(formatted_result)
        formatted_backend.append(backend_result)
    formatted_results_string = '\n\n'.join(formatted_results)
    formatted_results_backend = '\n\n'.join(formatted_backend)
    return formatted_results_backend, formatted_results_string