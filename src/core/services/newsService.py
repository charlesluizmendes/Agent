import httpx
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
                agent_type=AgentType.OPENAI_FUNCTIONS,
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
        try:
            url = f"https://html.duckduckgo.com/html/?q={topic}+notícias+2025"

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(url)
            response.raise_for_status()

            results = []
            for line in response.text.split("<a "):
                if "result__a" in line:
                    try:
                        title = line.split(">")[1].split("<")[0]
                        results.append(title)
                    except IndexError:
                        continue
                if len(results) >= 3:
                    break

            if not results:
                return "Nenhuma notícia encontrada."

            print(f"\n[DEBUG] Notícia encontrada: {results}")
            return "\n".join(results)

        except Exception as e:
            print(f"\n[ERRO] _add_file_from_chatpdf: {e}")
            raise

    @traceable(run_type="tool", name="summarize_news")
    async def _summarize_news(self, text):
        """Gera um resumo breve das notícias."""
        try:
            prompt = PromptTemplate.from_template(
                "Resuma as seguintes manchetes em português, destacando o tema principal e o contexto geral:\n\n{text}"
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            summary = await chain.arun({"text": text})

            print(f"\n[DEBUG] Resumo gerado: {summary}")
            return summary.strip()

        except Exception as e:
            print(f"\n[ERRO] _summarize_news: {e}")
            raise