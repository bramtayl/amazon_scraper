from os import path
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located as located,
)
from selenium.webdriver.support.wait import WebDriverWait as wait
from src.utilities import (
    FoiledAgainError,
    GoneError,
    get_filenames,
    new_browser,
    save_browser,
    switch_user_agent,
    wait_for_amazon,
    WAIT_TIME,
)


# product_url = product_url_data.loc[:, "product_url"][0]
def save_product_page(
    browser,
    product_id,
    product_url,
    product_pages_folder,
):
    if product_url.startswith("http"):
        browser.get(product_url)
    else:
        browser.get("https://www.amazon.com" + product_url)

    wait_for_amazon(browser)
    try:
        # wait for fakespot grade
        wait(browser, WAIT_TIME).until(
            located((By.CSS_SELECTOR, "div.fakespot-main-grade-box-wrapper"))
        )
    except TimeoutException:
        # might not be a fakespot grade
        pass

    save_browser(browser,
        path.join(product_pages_folder, product_id + ".html"),
    )


def save_product_pages(
    browser_box,
    product_url_data,
    product_pages_folder,
    user_agents,
    user_agent_index=0,
):
    browser = new_browser(user_agents[user_agent_index], fakespot=True)
    browser_box.append(browser)

    completed_product_filenames = get_filenames(product_pages_folder)

    # no previous product, so starts empty
    # product_url = product_url_data.loc[:, "url"][0]
    for product_id, product_url in zip(
        product_url_data.loc[:, "product_id"],
        product_url_data.loc[:, "product_url"],
    ):
        # don't save a product we already have
        if product_id in completed_product_filenames:
            continue

        try:
            save_product_page(
                browser,
                product_id,
                product_url,
                product_pages_folder,
            )
        except GoneError:
            # if the product is gone, print some debug information, and just continue
            print(product_url)
            print("Page no longer exists, skipping")
            continue
        except TimeoutException:
            # if the product times out, print some debug information, and just continue
            # come back to get it later
            print(product_url)
            print("Timeout, skipping")
            continue
        except FoiledAgainError:
            browser, user_agent_index = switch_user_agent(browser_box, browser, user_agents, user_agent_index)
            try:
                save_product_page(
                    browser,
                    product_id,
                    product_url,
                    product_pages_folder,
                )
            # hande the errors above again, except for the FoiledAgain error
            # if there's still a captcha this time, just give up
            except GoneError:
                print(product_url)
                print("Page no longer exists, skipping")
                continue
            except TimeoutException:
                print(product_url)
                print("Timeout, skipping")
                continue

    browser.close()
    browser_box.clear()

    return user_agent_index
