kutoka datetime agiza datetime

andika(datetime.now())

eleza jumla(x, y):
	rudisha x + y
	
andika(jumla(2, 5))

results = {'Tories': 368, 'Labour': 191, 'SNP': 55}
toa results['SNP']
andika(results)

kila party kwenye results:
	andika('{}: {} MPs'.format(party, results[party]))
	
userInput = 0
wakati userInput < 10:
	andika('Valid value')
	userInput = int(uliza('Please enter a number: '))
	ikiwa userInput > 8:
		andika('Close to the limit')
	lasivyo userInput == 0:
		andika('That is pretty low')
	isipokua:
		andika('Within normal range of values')
	
ikiwa 'SNP' haiko kwenye results:
	andika('Deletion successful')
isipokua:
	andika('Deletion failed')
	
a = Kweli

ikiwa a:
	andika('a is True')