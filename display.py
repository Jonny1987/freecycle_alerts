import webbrowser, logging, os

def display(groups):
	logging.error('displaying')
	cwd = os.getcwd()
	filename=cwd + '/results.html'

	# for group in groups:
	#     results[group.name] = [process(item.tag) for page in group.pages for item in page.items]

	result = """<html>
	<head>
	<link rel="stylesheet" type="text/css" href="freecycle.css">
	</head>"""

	for group in groups:
		for page in group.pages:
			for item in page.items:
				result += str(item.tag)
				result += '\n'
	result += '</html>'
	logging.error('displaying1')
	with open(filename, 'w') as file_:
		file_.write(result)
	logging.error('displaying2')
	browser = webbrowser.get('safari')

	browser.open_new(filename)


	