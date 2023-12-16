import asyncio
from pyppeteer import launch
import json

async def scrape_market_information(sem, link):
    async with sem:
        browser = await launch()
        try:
            page = await browser.newPage()
            await page.goto(link)

            """title = await page.title()
            print('Page title:', title)"""

            length_1 = await page.evaluate('document.querySelectorAll("body > section > div.row > div.col-12.col-lg-8.col-content > div:nth-child(3) > div > div:nth-child(1) > div.p-3 > div.flex-list-2-col.flex.justify-content-between.data-info-ul-box-m > ul:nth-child(1) > li").length')
            length_2 = await page.evaluate('document.querySelectorAll("body > section > div.row > div.col-12.col-lg-8.col-content > div:nth-child(3) > div > div:nth-child(1) > div.p-3 > div.flex-list-2-col.flex.justify-content-between.data-info-ul-box-m > ul:nth-child(2) > li").length')

            base_path_1 = "body > section > div.row > div.col-12.col-lg-8.col-content > div:nth-child(3) > div > div:nth-child(1) > div.p-3 > div.flex-list-2-col.flex.justify-content-between.data-info-ul-box-m > ul:nth-child(1)"
            base_path_2 = "body > section > div.row > div.col-12.col-lg-8.col-content > div:nth-child(3) > div > div:nth-child(1) > div.p-3 > div.flex-list-2-col.flex.justify-content-between.data-info-ul-box-m > ul:nth-child(2)"

            info_dict = {}

            for idx in range(2, length_1 + 1):
                name = await page.evaluate(f'document.querySelector("{base_path_1} > li:nth-child({idx}) > span:nth-child(1)").textContent')
                value = await page.evaluate(f'document.querySelector("{base_path_1} > li:nth-child({idx}) > span:nth-child(2)").textContent')

                info_dict[name] = value

            for idx in range(1, length_2 + 1):
                name = await page.evaluate(f'document.querySelector("{base_path_2} > li:nth-child({idx}) > span:nth-child(1)").textContent')
                value = await page.evaluate(f'document.querySelector("{base_path_2} > li:nth-child({idx}) > span:nth-child(2)").textContent')

                info_dict[name] = value

            return link, info_dict

        except Exception as e:
            print(f"Error in scrape_market_information: {e}")
            return link, {}

        finally:
            await browser.close()

async def main():
    sem = asyncio.Semaphore(5)
    browser = await launch()
    
    try:
        page = await browser.newPage()
        await page.goto('https://finans.mynet.com/borsa/hisseler/')

        title = await page.title()
        print('Page title:', title)

        length = await page.evaluate('document.querySelectorAll("body > section > div.row > div.col-12.col-lg-8.col-content > div:nth-child(3) > div > div > div.table-scrollable-mobil > div > table > tbody > tr").length')

        all_links = []
        all_links_base = 'body > section > div.row > div.col-12.col-lg-8.col-content > div:nth-child(3) > div > div > div.table-scrollable-mobil > div > table > tbody'

        base_dict = dict()

        for idx in range(1, 10):
            information_selector = await page.evaluate(f'document.querySelector("{all_links_base} > tr:nth-child({idx}) > td:nth-child(1) > strong > a").href')
            all_links.append(information_selector)
    
        tasks = [scrape_market_information(sem, elm) for elm in all_links]
        results = await asyncio.gather(*tasks)

        for link, this_market_dict in results:
            name_string = link[39:]
            base_dict[name_string] = this_market_dict

        with open("output//sample.json", "w", encoding="utf-8") as outfile:
            json.dump(base_dict, outfile, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error in main: {e}")

    finally:
        await browser.close()

asyncio.get_event_loop().run_until_complete(main())
