#!/usr/bin/python3
import sys

usage = {}
WEAPONS = ['gs', 'ls', 'sns', 'db', 'hammer', 'hh', 'lance',
		   'gl', 'sa', 'ca', 'ig', 'lbg', 'hbg', 'bow']
try:
	with open(sys.argv[1], 'r') as f:
		game = ""
		for line in f:
			if line.startswith('['):
				game = line[1:-2]
				usage[game] = {}
				for weapon in WEAPONS:
					usage[game][weapon] = 0 #dummy value for older games
				print("Game name: " + line[1:-2])
			else:
				try:
					weapon, ammount = line.split('=')
					usage[game][weapon.strip()] = ammount.strip()
				except ValueError:
					pass
except FileNotFoundError:
	print(f'no such file {sys.argv[1]} found')
	sys.exit()

with open('style_gen.css', 'w') as outfile:
	outfile.write(':root {\n') #attach all counters to :root element for global access
	tags = []
	for game in usage:
		tag = "".join([x[0] for x in game.split()]).lower() #"Monster Hunter World" becomes "mhw"
		tags.append(tag)
		outfile.write(f'    --{tag}-enabled : 1;\n')
		for weapon in usage[game]:
			count = usage[game][weapon]
			outfile.write(f'    --{tag}-{weapon}: {count};\n')
	wepstrings = {} #dictionary for later drop-in replacement
	countmaxstr = '--count-max: max('
	for weapon in WEAPONS:
		weaponstring=('calc(')
		for i in range(len(tags)):
			#generate a calc()-formula to sum up the usage stats for a weapon with regards
			#to all enabled games.
			weaponstring += f'calc(var(--{tags[i]}-{weapon}) * var(--{tags[i]}-enabled))'
			if i < len(tags) - 1:
				weaponstring += ' + '
			else:
				weaponstring += ')'
		wepstrings[weapon] = weaponstring #store in our dictionary for later
		countmaxstr += f'{weaponstring}\n' + ' '*21 #and attach to the max-count function
		if weapon != 'bow': #the last weapon in the list is always bow
			countmaxstr += ','
	with open('style_src.css', 'r') as infile:
		text = infile.read()
		for weapon in WEAPONS:
			#--count-{weapon} isnt declared; it's a placeholder for this replacement to fill
			text = text.replace(f'var(--count-{weapon})', wepstrings[weapon])
		#same thing as above, except /*%count-max%*/ is commented out by default in case of a faulty fill
		text = text.replace('/*%count-max%*/', countmaxstr+',1);')
		#wire up the input toggles
		switchstr = ''
		for i in range(len(tags)):
			switchstr += 'input:not(:checked) +*+' + '*+*+' * (len(tags)-(i+1)) + ' #weapon{\n'
			switchstr += f'    --{tags[i]}-enabled: 0;\n}}' #double curlie is escaped } in f-string
		text = text.replace('/*%inputs%*/', switchstr)
		outfile.write(text)
	with open('card.html', 'w') as html_out:
		with open('card_src.html', 'r') as infile:
			text = infile.read()
			#wire up the input toggles
			switchstr = ''
			for tag in tags:
				switchstr += f'    <input class="switches" type="checkbox" id="{tag}" name="{tag.upper()}" checked>\n'
				switchstr += f'    <label class="switches" for="{tag}">{tag.upper()}</label>\n'
			text = text.replace('<!--SWITCHES-->', switchstr)
			html_out.write(text)