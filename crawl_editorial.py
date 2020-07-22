from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import openpyxl

try:
    wb = openpyxl.load_workbook('raw_dataset_add.xlsx')
    sheet = wb.active
    print('불러오기 성공!')
except:
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(['Keyword', 'Source', 'Date', 'Title', 'Content', 'Pos'])
    print('신규 파일 생성!')

driver = webdriver.Chrome('chromedriver.exe')
driver.get('https://www.kinds.or.kr/')

# 검색 기간 200716 기준 3년으로
begin_date = '2017-07-16'
end_date = '2020-07-16'

date_filter = driver.find_element_by_css_selector('button#date-filter-btn')
begin_date_input = driver.find_element_by_id('search-begin-date')
end_date_input = driver.find_element_by_id('search-end-date')

date_filter.click()

begin_date_input.send_keys(Keys.CONTROL + "a")
begin_date_input.send_keys(Keys.DELETE)
begin_date_input.send_keys(begin_date)

end_date_input.send_keys(Keys.CONTROL + "a")
end_date_input.send_keys(Keys.DELETE)
end_date_input.send_keys(end_date)

#confirm = driver.find_element_by_css_selector('button#date-confirm-btn')
#confirm.click()
time.sleep(1)

# 사설 섹션 선택
detail_filter = driver.find_element_by_css_selector('button#detail-filter-btn')
editorial = driver.find_element_by_css_selector('input#search-index-type-editorial')

detail_filter.click()
editorial.click()

# 제목에만 범위 한정
select_scope = Select(driver.find_element_by_id('search-scope-type-editorial'))
select_scope.select_by_value('2')

# 검색버튼
driver.find_element_by_css_selector('button.news-search-btn').click()
time.sleep(5)

# 100건씩 보기
article_per_page = Select(driver.find_element_by_id('select2'))
article_per_page.select_by_value('100')
time.sleep(3)

keywords = ['필요한 키워드 추가']

for keyword in keywords:
    # 검색어 입력창 열고 검색어 입력
    driver.find_element_by_css_selector('div#headingOne a').click()
    time.sleep(1)

    search_input = driver.find_element_by_css_selector('input#total-search-key')
    search_input.clear()  # 루프 돌면서 검색어를 다시 입력하면 검색어가 쌓이므로 입력창 비우는 코드 추가
    search_input.send_keys(keyword)

    # 검색 버튼
    driver.find_element_by_css_selector('button.news-search-btn').click()
    time.sleep(10)

    # 페이지 수 체크 (기사 수)
    n_of_article = int(driver.find_element_by_css_selector('span#total-news-cnt').text)

    if n_of_article % 100 == 0:
        n_of_page = n_of_article // 100
    else:
        n_of_page = n_of_article // 100 + 1

    for page in range(n_of_page):

        # 페이지별 사설 수집
        container = driver.find_elements_by_css_selector('div.news-item__body')

        for cont in container:

            try:
                source = cont.find_element_by_css_selector('a').text
            except:
                source = cont.find_element_by_css_selector('div.news-item__meta').text
                cut = source.find(' ')
                source = source[:cut]

            date = cont.find_element_by_css_selector('span.news-item__date').text

            element = cont.find_element_by_class_name('news-item__title')
            driver.execute_script("arguments[0].click();", element)

            time.sleep(3)
            article = driver.find_element_by_css_selector('div#news-detail-modal div.modal-content')

            # 제목, 본문
            title = article.find_element_by_css_selector('h4').text.strip()
            content = article.find_element_by_css_selector('div.news-detail__content').text.strip()

            tags = ['[사설]', '[fn사설]', '<사설>', '(사설)', '[사 설]']

            for tag in tags:
                title = title.replace(tag, '')

            title.strip()
            print(keyword, source, date, title)
            print("=" * 50)

            sheet.append([keyword, source, date, title, content])

            article.find_element_by_css_selector('button.close').click()
            time.sleep(1)

        page_bar = driver.find_elements_by_css_selector('ul.pagination > li > a')
        # 마지막 페이지인지 체크
        if page == n_of_page - 1:
            wb.save('raw_dataset.xlsx')
            break
        else:
            # 마지막 페이지 아닐 경우 다음 페이지 클릭
            page_bar[page+3].click()
            time.sleep(10)

