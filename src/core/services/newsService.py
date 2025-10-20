import requests
import asyncio

from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from src.core.common.result import Result
from src.core.models.news import NewsInputModel, NewsOutputModel
from src.core.interfaces.services.newsService import INewsService


class NewsService(INewsService):
    def __init__(
        self,
        model: str,
        api_key: str,
        temperature: float
    ):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature
        )

    @traceable(run_type="chain", name="run_news_agent")
    async def run(self, dto: NewsInputModel) -> Result[NewsOutputModel]:
        try:
            def run_async(coro):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    return asyncio.ensure_future(coro)
                else:
                    return asyncio.run(coro)

            tools = [
                Tool(
                    name="search_news",
                    description="Busca as 3 notícias mais recentes sobre um tema na web.",
                    func=lambda *_, **__: run_async(self._search_news(dto.topic)),
                ),
                Tool(
                    name="summarize_news",
                    description="Gera um resumo em português sobre as notícias encontradas.",
                    func=lambda text, *_, **__: run_async(self._summarize_news(text)),
                )
            ]

            agent = initialize_agent(                
                llm=self.llm,
                tools=tools,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                handle_parsing_errors=True,
                verbose=True,
            )

            task = f"""
                Siga as etapas:
                1. Use 'search_news' para buscar as 3 notícias mais recentes sobre o tema.
                2. Use 'summarize_news' para gerar um resumo em português das notícias encontradas.
                3. Responda de forma organizada, no formato:
                    - Título 1
                    - Título 2
                    - Título 3
                    Resumo: <resumo em até 5 linhas>
            """

            response = await agent.ainvoke({"input": task})
            content = response.get("output", "").strip()

            output = NewsOutputModel(content=content)
            return Result.ok(data=output)

        except Exception:
            raise


    @traceable(run_type="tool", name="search_news")
    async def _search_news(self, topic):
        """Busca notícias recentes sobre um tema (usando DuckDuckGo)."""
        url = f"https://duckduckgo.com/html/?q={topic}+notícias+2025"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return "Falha ao buscar notícias."

        results = []
        for line in r.text.split("<a "):
            if "result__a" in line:
                try:
                    title = line.split(">")[1].split("<")[0]
                    results.append(title)
                except IndexError:
                    continue
            if len(results) >= 3:
                break
        return "\n".join(results)

    @traceable(run_type="tool", name="summarize_news")
    async def _summarize_news(self, news_text):
        """Gera um resumo breve das notícias."""
        prompt = PromptTemplate.from_template(
            "Resuma as seguintes manchetes em português, destacando o tema principal e o contexto geral:\n\n{news_text}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        summary = await chain.arun({"news_text": news_text})
        return summary.strip()