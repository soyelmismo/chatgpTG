from itertools import islice
from duckduckgo_search import DDGS
async def search(self, prompt):
    resultados=[]
    with DDGS() as ddgs:
        ddgs_gen = ddgs.text(prompt, backend="lite", region=f'{self.lang}-{self.lang}', safesearch='Off', timelimit='y')
        for r in islice(ddgs_gen, 5):
            resultados.append(r)
    formatted_results = []
    for resultado in resultados:
        title = resultado['title']
        href = resultado['href']
        body = resultado['body']
        formatted_result = f"[{title}]({href}): {body}"
        formatted_results.append(formatted_result)
    formatted_results_string = '\n\n'.join(formatted_results)

    return formatted_results_string