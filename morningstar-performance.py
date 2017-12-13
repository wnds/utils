from numpy import nan
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
 

def extractCurrentPageData(pageData, browser, columnNames):
	tableRowsSelector = "#ctl00_ContentPlaceHolder1_msStockQuickrankControl_gridResult tr"
	tableRows = browser.find_elements_by_css_selector(tableRowsSelector)

	for tableRow in tableRows:
		rowData = {}

		tableColumns = tableRow.find_elements_by_css_selector("td")
		
		columnIndex = 0
		
		for tableColumn in tableColumns:
			if tableColumn.text != '':
				rowData[columnNames[columnIndex]] = tableColumn.text
				columnIndex = columnIndex + 1
		
		if bool(rowData):
			pageData.append(rowData)


def navigateToNextPage(browser):
	nextPageCSSSelector = '#ctl00_ContentPlaceHolder1_msStockQuickrankControl_AspNetPager > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > a:nth-child(5)'
	nextPageLinkElement = browser.find_element_by_css_selector(nextPageCSSSelector)
	if nextPageLinkElement:
		ActionChains(browser).move_to_element(nextPageLinkElement).click().perform()


def main():
	## launch the Chrome browser   
	browser = webdriver.Chrome(executable_path="chromedriver")
	browser.maximize_window()
	 
	url = "http://lt.morningstar.com/dk7pkae7kl/stockquickrank/default.aspx"
	browser.get(url)

	promotionPath = "a#TabPerformance"
	promotionTab = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, promotionPath))).text

	ActionChains(browser).move_to_element(browser.find_element_by_css_selector(promotionPath)).click().perform()

	tableHeaderSelector = "#ctl00_ContentPlaceHolder1_msStockQuickrankControl_gridResult tr th"
	tableHeaders = browser.find_elements_by_css_selector(tableHeaderSelector)

	columnNames = []
	for tableHeader in tableHeaders:
			if tableHeader.text != '':
				columnNames.append(tableHeader.text)

	print('Column names {0}').format(columnNames)

	# text like  'Total Results: 5110'
	totalRows = int(browser.find_element_by_css_selector('#ctl00_ContentPlaceHolder1_msStockQuickrankControl_pnlTotalResults')
		.text.split(": ")[1])

	pageData = []

	extractCurrentPageData(pageData, browser, columnNames)

	while len(pageData) <= totalRows:

		print ('Current pageData.length is {0} as compared to totalRows {1}').format(len(pageData), totalRows);

		extractCurrentPageData(pageData, browser, columnNames)
		
		navigateToNextPage(browser)

	browser.quit()

	df = pd.DataFrame(pageData)
	 
	## create a csv file in our working directory with our scraped data
	df.to_csv("test.csv", index=False)

if __name__ == '__main__':
    main()
