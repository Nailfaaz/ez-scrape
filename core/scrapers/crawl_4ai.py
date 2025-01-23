from crawl4ai.async_webcrawler import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher, CrawlerMonitor, DisplayMode, RateLimiter
import asyncio
import logging

class Crawl4aiCrawler:
    def __init__(self,max_retries,max_session,memory_threshold):
        self.max_retries=max_retries
        self.max_session=max_session
        self.memory_threshold=memory_threshold
        self.browser_config, self.dispatcher = self._create_config()
        logging.info("Crawler initialized with configurations.")
 
    def _create_run_config(self,css_selector) :
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            stream=False,
            css_selector=css_selector)
        return run_config
    def _create_browser_config(self) :
        browser_config = BrowserConfig(
        verbose=False, 
        text_mode=True, 
        light_mode=True
    )
        return browser_config
    
    def _create_dispatcher(self) :
        dispatcher = MemoryAdaptiveDispatcher( 
        memory_threshold_percent=self.memory_threshold, # threshold bisa diubah
        check_interval=1.0,
        max_session_permit=self.max_session, # bisa diganti
        monitor=CrawlerMonitor(
            display_mode=DisplayMode.DETAILED
        ),
        rate_limiter=RateLimiter(      
            base_delay=(1.0, 2.0),
            max_delay=30.0,
            max_retries=self.max_retries # bisa diubah
        ),
        )
        return dispatcher
    def _create_config(self) :
        browser_config = self._create_browser_config()
        dispatcher=self._create_dispatcher()
        return browser_config,dispatcher


    async def crawl_batch(self,urls,css_selector):


        
    #     run_config = CrawlerRunConfig(
    #         cache_mode=CacheMode.BYPASS,
    #         stream=False,
    #         css_selector=css_selector # CSS selector bisa diganti
    #     )
        
    

    



    # dispatcher = MemoryAdaptiveDispatcher( 
    #     memory_threshold_percent=80.0, # threshold bisa diubah
    #     check_interval=1.0,
    #     max_session_permit=50, # bisa diganti
    #     monitor=CrawlerMonitor(
    #         display_mode=DisplayMode.DETAILED
    #     ),
    #     # rate_limiter=RateLimiter(      
    #     #     base_delay=(1.0, 2.0),
    #     #     max_delay=30.0,
    #     #     max_retries=2 # bisa diubah
    #     # ),
    # )

        async with AsyncWebCrawler(config=self.browser_config) as crawler:

            results = await crawler.arun_many(
                urls=urls,
                config=self._create_run_config(css_selector),
                dispatcher=self.dispatcher
            )

            # for result in results:
            #     if result.success:
            #         print(result.cleaned_html[:500]) 
            #         print("=============================================")
            #     else:
            #         print(f"Failed to crawl {result.url}: {result.error_message}")

            

            all_links = []
            for result in results:
                if result.success:
                    all_links.extend([ele["href"] for ele in result.links["internal"]])
                else:
                    print(f"Failed to crawl {result.url}: {result.error_message}")
            return all_links
    def run_scrap(self,urls,css_selector) :
        return asyncio.run(self.crawl_batch(urls,css_selector))
    
# if __name__ == "__main__":
#     css_selector = "h3.gdlr-core-blog-title.gdlr-core-skin-title a"
#     pagination_link = "https://www.senibudayabetawi.com/page/{page_number}"
#     max_pages = 10
#     crawler=Crawl4aiCrawler(css_selector=css_selector, pagination_link=pagination_link, max_pages=max_pages)
#     # results = asyncio.run(crawl_batch(css_selector=css_selector, pagination_link=pagination_link, max_pages=max_pages))
#     results = crawler.run_scrap()

#     print(results[:10])
#     print(f"Num links: {len(results)}")
