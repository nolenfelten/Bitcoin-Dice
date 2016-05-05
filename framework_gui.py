from __future__ import unicode_literals
from Tkinter import *
import ttk as ttk
from PIL import ImageTk, Image
import os, math, tkFont, base64, time, json, requests, Queue, thread
import config



class ProjectDiceBot:
	
	def __init__(self, Queue):

		
		
		self.url_POST_register = 'https://api.primedice.com/api/register'
		self.url_POST_login = 'https://api.primedice.com/api/login'
		self.url_POST_bet = 'https://api.primedice.com/api/bet'
		self.url_GET_logout = 'https://api.primedice.com/api/logout'	
		self.url_GET_info = 'https://api.primedice.com/api/users/1'
		self.url_GET_affiliate = 'https://api.primedice.com/api/affiliates/1'
		self.withdraw_affiliate = "https://api.primedice.com/api/affiliate/withdraw" #Withdraw Affiliate POST URL. Expects amount.

		
		#Bet Counter
		self.bet_count = 0




	def loginbox(self):
		#Open window, Login to Primedice
		login_box = Tk()
		login_box.title('Login')
		login_box.geometry("180x90")
		
		box = Frame(login_box)
		box.pack()

		lblUsername = LabelFrame(box, text = "Username:", labelanchor = 'w', bd = 0)
		lblPassword = LabelFrame(box, text = "Password:", labelanchor = 'w', bd = 0)
		
		entUsername = Entry(lblUsername, width = 15)
		entPassword = Entry(lblPassword, width = 15)

		lblUsername.pack()
		lblPassword.pack()
		entUsername.pack(side = 'right')
		entPassword.pack(side = 'right')
		
		post_body = {
			'username': user.get(),
			'password': word.get(), 
			'opt': ''
		}
			
			
		#POST login info and retrieve access token
		btn = Button(login_box, text = "Login", fg = "#A1DBCD", bg = "#383A39", command = lambda attempt: self.session_post(self.url_POST_login, post_body))
		btn.pack()
		
		login_box.mainloop()













class Main:
	
	def __init__(self, dataQueue):
		
		self.dataQueue = dataQueue
		self.root = Tk()
		self.root.title('Dice Framework')	# Set window title and size
		
		self.work_tokens = []
		self.mastertoken = []
		self.masterloggedin = False
		self.kill_army = False
		self.bet_tick = 0
		self.master_balance = "0.00000000"
		self.balance = "0.00000000"
		
		
		#Start HTTP session
		self.session = requests.Session()
		#HTTP Headers
		self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.130 Chrome/43.0.2357.130 Safari/537.36'}

		#Loading Images
		self.overview_bg = ImageTk.PhotoImage(file = './images/super_mario_by_xxlightsourcexx.jpg')
		self.imageoptionlib = ImageTk.PhotoImage(file = './images/options.jpg')
		self.calcimg = ImageTk.PhotoImage(file = './images/40833_super_mario_bros_bowser.jpg')
		self.imageloglib = ImageTk.PhotoImage(file = './images/snes.png')
		
		# Master container
		self.window = Frame(self.root, bg = 'black')
		
		
		
		
		
		# Root => Header 
		self.frame_header = Frame(self.window, bg = "black")
		

		
		# Clock Box
		self.clocklblFrame = LabelFrame(self.frame_header, text = "Current Time:", font = ('Helvectica', 13, 'bold'), labelanchor = 'nw', bd = 3, bg = "black", fg = "white")
		self.clocklbl = Label(self.clocklblFrame, font = ('Helvectica', 16, 'bold'), bg = "#000000", fg = "#FFFFFF")
		# Wagered Box
		self.totalWageredFrame = LabelFrame(self.frame_header, text = "Total Wagered:", font = ('Helvectica', 13, 'bold'), labelanchor = 'nw', bd = 3, bg = "black", fg = "#8888FF")
		self.totalWageredlbl = Label(self.totalWageredFrame, text = str(self.balance), font = ('Impact', 15, 'bold'), bg = "#000000", fg = "#FFFFFF", width = 20)		
		# Affiliate Box
		self.affiliateFrame = LabelFrame(self.frame_header, text = "Affiliate Balance:", font = ('Helvectica', 13, 'bold'), labelanchor = 'nw', bd = 3, bg = "black", fg = "#8888FF")
		self.affiliatelbl = Label(self.affiliateFrame,  text = '0', font = ('Impact', 15, 'bold'), bg = "#000000", fg = "#00FF00")
		# Bet Count Box
		self.betcountFrame = LabelFrame(self.frame_header, text = "Bet Counter:", font = ('Helvectica', 13, 'bold'), labelanchor = 'nw', bd = 3, bg = "black", fg = "#8888FF")
		self.betcountlbl = Label(self.betcountFrame, text = "0", font = ('Impact', 15, 'bold'), bg = "#000000", fg = "#FFFFFF")		
		# Mouse Debug Box
		self.mousedebugFrame = LabelFrame(self.frame_header,  text = "[Dev] Mouse:", font = ('Helvectica', 10, 'bold'), labelanchor = 'nw', bd = 3, bg = "black", fg = "#8888FF", width = 30)
		self.mousedebugLblX = Label(self.mousedebugFrame, text = "X: -", font = ('Helvectica', 9, 'bold'), bg = "#00000F", fg = "#00FFFF")
		self.mousedebugLblY = Label(self.mousedebugFrame, text = "Y: -", font = ('Helvectica', 9, 'bold'), bg = "#00000F", fg = "#FF00FF")
		
		
		
		self.frame_header.pack(side = "top", fill = 'both', padx = 290)
		self.clocklblFrame.pack(side = 'left')
		self.clocklbl.pack() 
		self.totalWageredFrame.pack(side = 'left')
		self.totalWageredlbl.pack()
		self.affiliateFrame.pack(side = 'left')
		self.affiliatelbl.pack()
		self.betcountFrame.pack(side = 'left')
		self.betcountlbl.pack()	
		self.mousedebugFrame.pack(side = 'left', padx = 30)
		self.mousedebugLblX.pack(side = 'right')
		self.mousedebugLblY.pack(side = 'left')
		


		
		
		

		
		
		
		
		


		
		# Body
		self.notebook = ttk.Notebook(self.window, height = 920, width = 1360)
		tab_style = ttk.Style()
		tab_style.configure("TNotebook", background = "black", borderwidth = 0)

		
		
		# Body -> Overview Tab
		self.overview = ttk.Frame(self.notebook, style = 'Tab1.TFrame')
		self.imagelbl = Label(self.overview, image = self.overview_bg).place(relx = 0, rely = 0, y = 0, relwidth = 1, relheight = 1)
		
		
		
		# Overview Tab -> Master
		self.master_bot = LabelFrame(self.overview, width = 130, height = 50, text = "Main Account", bg = '#DCF4FF', font = ('Digital-7', 10))
		
		self.boxy = Frame(self.master_bot, bg = '#DCF4FF')
		self.login_master = Button(self.boxy, text = "Login", fg = "#a1dbcd", bg = "#383a39", width = 10, command = lambda: self.login_box())
		self.logout_master = Button(self.boxy, text = "Create User", fg = "#a1dbcd", bg = "#383a39", width = 10, command = lambda: self.signup_box())
		self.masteruser = Label(self.boxy, fg = "#7733FF", text = "", bg = "#DCF4FF", width = 10)
		#self.si_master = Button(self.boxy, text = "Create User", fg = "#a1dbcd", bg = "#383a39", width = 10, command = lambda: self.signup_box(master = True))
		
		self.boxxy = Frame(self.master_bot, bg = '#DCF4FF')
		self.master_balance_lbl = Label(self.boxxy, text = "Balance", fg = "#7733FF", bg = '#DCF4FF', font = ('Times', 13, 'bold'))
		self.master_balance_lbl1 = Label(self.boxxy, text = str(self.balance), fg = "#7777FF", bg = '#DCF1FF', width = 10, font = ('Aerial', 14, 'bold'))
		
		self.boxxxy = Frame(self.master_bot, bg = '#DCF4FF')
		self.predictionlbl = Label(self.boxxxy, text = "Prediction:", fg = "#7733FF", bg = '#DCF4FF', width = 10, font = ('Times', 13, 'bold', 'italic'))
		self.predictionent = Entry(self.boxxxy, fg = "#7777FF", bg = '#DCF4FF', width = 5)
		self.predictionent.insert('end', "49.95")
		self.amountlbl = Label(self.boxxxy, text = " Bet Amount:", fg = "#7733FF", bg = '#DCF4FF', width = 10, font = ('Times', 13, 'bold', 'italic'))
		self.amountent = Entry(self.boxxxy, fg = "#7777FF", bg = '#DCF4FF', width = 5)
		self.amountent.insert('end', "0")
		
		self.boxxxxy = LabelFrame(self.master_bot, bg = '#DCF4FF', text = 'Bet:', bd = 1, fg = "#7722FF", font = ('Times', 13, 'bold', 'italic'))
		self.hi = Button(self.boxxxxy, text = "Hi", fg = "#FFFFFF", bg = "#7777FF", font = ('Helvectica', 10, 'bold'), width = 10, command = lambda amount = self.amountent.get(), target = self.predictionent.get(): self.bet(condition = "<", target = target, amount = amount))
		self.lo = Button(self.boxxxxy, text = "Lo", fg = "#FFFFFF", bg = "#7777FF", font = ('Helvectica', 10, 'bold'), width = 10, command = lambda amount = self.amountent.get(), target = self.predictionent.get(): self.bet(condition = "<", target = target, amount = amount))
		
		
		self.logg = LabelFrame(self.overview, bg = '#DCF4FF')
		self.text = Text(self.logg, height = 10, width = 50)
		self.text.tag_config('newline', background = 'grey')
		self.scroller = Scrollbar(self.logg)
		self.text.config(yscrollcommand = self.scroller.set)
	#	if config.master_token != '':
		
	
		self.master_bot.place(x = 45, y = 5)
		self.boxy.pack(side = 'left', padx = 15)
		self.masteruser.pack(pady = 3, ipady = 1)
		self.login_master.pack()
		self.logout_master.pack(pady = 3)
		self.boxxy.pack(side = 'left', padx = 10, pady = 1)
		self.master_balance_lbl.pack(pady = 2)
		self.master_balance_lbl1.pack()
		self.boxxxy.pack(side = 'left', padx = 5, pady = 1)
		self.predictionlbl.pack()
		self.predictionent.pack()
		self.amountlbl.pack(pady = 0)
		self.amountent.pack(pady = 9)
		self.boxxxxy.pack(side = 'left', padx = 5, pady = 1)
		self.hi.pack(side = 'left', padx = 5, pady = 2)
		self.lo.pack(side = 'right', padx = 5, pady = 2)
		self.logg.place(x = 700, y = 10)
		self.text.pack(side = 'left')
		self.scroller.pack(side = 'left', fill = 'both')
		
		
		
		
		
	
	
	
		# Options Tab
		self.options = ttk.Frame(self.notebook, style = 'Tab1.TFrame')
		self.imageoptionlbl = Label(self.options, image = self.imageoptionlib).place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
		
		
		
		
		
		
		
		
		
		
		# Calculator Tab
		self.calc_tab = ttk.Frame(self.notebook, style = 'Tab1.TFrame')
		self.calclbl = Label(self.calc_tab, image = self.calcimg).place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
		self.calc1 = Button(self.calc_tab, text = "Loss Streak Probability", fg = "#FF0000", bg = "#F3A60D", command = lambda: self.loss_streak_calc())
		self.calc1.place(x = 145, y = 30)
		self.calc2 = Button(self.calc_tab, text = "% Increase vs Multiplier", fg = "#FF0000", bg = "#F3A60D", command = lambda: self.inc_multi_calc())
		self.calc2.place(x = 285, y = 30)

		
		
		
		
		
		
		# Pack tabs into view
		self.notebook.add(self.overview, text = "Overview")
		self.notebook.add(self.options, text = "Options")
		self.notebook.add(self.calc_tab, text = "Calculators")
		self.root.state('zoomed') 	# Window state: Maximized
		self.root.bind("<Motion>", self.debug_mouse)
		self.tick()
		self.poll()
		self.notebook.pack()
		self.window.pack(fill = 'both')
		self.root.mainloop()

		
	def tick(self):
		#Clock
		if time.strftime('%H:%M:%S') != "0":
			self.clocklbl.config(text = time.strftime('%H:%M:%S'))	
		self.clocklbl.after(200, self.tick)
	
	
	def debug_mouse(self, event):
		xx, yy = event.x, event.y
		x_str = "X: %d" % (xx)
		y_str = "Y: %d" % (yy)
		self.mousedebugLblX['text'] = x_str
		self.mousedebugLblY['text'] = y_str
		
		
	def pop_up(self, text):
		#Error Pop up window
		popup = Tk()
		popup.geometry("50x50")
		popup.title('Notice')
		
		bit = Label(popup, bitmap = "hourglass")
		lbl = Label(popup, text = text).place(x = 8, y = 8)
		
		btnexit = Button(popup, text = "Close" , command = lambda: popup.destroy()).place(x = 20, y = 35)
		popup.mainloop()

		
	def poll(self):
		try:
			data = self.dataQueue.get_nowait()
		except Queue.Empty:
			pass
		else:
			self.text.tag_remove('newline', '1.0', 'end')
			position = self.scroller.get()
			self.text.insert('end', '%s\n' %(data), 'newline')            
			if (position[1] == 1.0):
				self.text.see('end')
			self.root.after(1000, self.poll)

		
		
	def session_post(self, url, post):
		try:
			#Send the bet through our self.session
			self.attempt = self.session.post(url, data = post, headers = self.headers)
		
			return self.attempt
		
		except:
			print self.attempt.status_code
						
	def signup_box(self, master = False):
		#Open window, Create Primedice User
		sign_up = Tk()
		sign_up.title('Sign Up')
		sign_up.geometry("180x90")
		
		sign = Frame(sign_up)
		sign.pack()

		lblUsername = LabelFrame(sign, text = "Username:", labelanchor = 'w', bd = 0)
		lblPassword = LabelFrame(sign, text = "Password:", labelanchor = 'w', bd = 0)
		lblAfiliate = LabelFrame(sign, text = "Affilate:", labelanchor = 'w', bd = 0)
		
		entUsername = Entry(lblUsername, width = 15)
		entPassword = Entry(lblPassword, width = 15)
		entAfiliate = Entry(lblAfiliate, width = 5)
		entAfiliate.insert(0, "Nolen")

		lblUsername.pack()
		lblPassword.pack()
		lblAfiliate.pack()
		entUsername.pack(side = 'right')
		entPassword.pack(side = 'right')
		entAfiliate.pack(side = 'right')

		
		def signupp(self = self, master = False):
			url = 'https://api.primedice.com/api/register'
			post_body = {'username': entUsername.get(), 'password': entPassword.get(), 'affiliate': entAfiliate.get()}
			
			feedback = self.session_post(url, post_body)
			
			print entUsername.get() + " : "+ self.token
			open("tokens.txt", 'a').write(entUsername.get() + ":" + entPassword.get() + " = " + self.token + "\n")
			
			self.workers.append(self.token)
			self.tokens.append(feedback.content.split('access_token":"')[1].split('"')[0])
			sign_up.destroy
		
		#Send POST request
		btn = Button(sign, text = "Sign Up!", fg = "#A1DBCD", bg = "#383A39", command = lambda: signupp()).pack()

	def bet(self, amount = 0, target = 95, condition = "<"):
		try:
			target = float(target) # Bet on
			amount = int(amount) # Bet price
		except:
			return "Target must be an integer!"
		
		if not condition in ["<",">"]:
			print "Wrong condition. Must be either > or <"
		else:
			#Fill the form
			post_data = {'amount': str(amount),'condition': str(condition),'target': str(target)}
			if self.mastertoken[0]:
			
				#Send The Request
				self.place_bet = self.session_post('https://api.primedice.com/api/bet?access_token=' + self.mastertoken[0], post = post_data)
				#If all good
				if self.place_bet.status_code == 200:
			
					#Load into JSON
					bet_response = json.loads(self.place_bet.content)
					feedback = {
						'jackpot': bet_response["bet"]["jackpot"],
						'win': bet_response["bet"]["win"],
						'amount': bet_response["bet"]["amount"],
						'roll': bet_response["bet"]["roll"],
						'profit': bet_response["bet"]["profit"],
						'balance': bet_response["user"]["balance"]
					}
			
					if feedback["win"]:	
						self.master_balance_lbl1['text'] = feedback['balance']
						self.master_green()
					else:
						self.master_balance_lbl1['text'] = feedback['balance']
									
				elif self.place_bet.status_code == 400 and self.place_bet.content == "Insufficient funds":
					self.pop_up("Insufficient Funds")
				
				else:
					self.bet(amount, target, condition)
		
	def army_bet(self, amount = 0, target = 95, condition = "<"):
		
		#Check Curcuit Breaker FIRST!
		if self.kill_army == False:
			#Check if there are any bot tokens in the array
			if self.worker_tokens.length != 0:
		
				params = {
					'access_token': self.worker_tokens
				}
				
	def master_green(self):
		
		if self.master_balance_lbl1['fg'] == "#7777FF":
			self.master_balance_lbl1['fg'] = "#7070BB"
		else:
			if self.master_balance_lbl1['fg'] == "#009900":
				self.master_balance_lbl1['fg'] = "#00FF00"
			if self.master_balance_lbl1['fg'] == "#007000":
				self.master_balance_lbl1['fg'] = "#009900"
			if self.master_balance_lbl1['fg'] == "#004000":
				self.master_balance_lbl1['fg'] = "#007000"
			if self.master_balance_lbl1['fg'] == "#101019":
				self.master_balance_lbl1['fg'] = "#004000"	
			if self.master_balance_lbl1['fg'] == "#202099":
				self.master_balance_lbl1['fg'] = "#101019"
			if self.master_balance_lbl1['fg'] == "#7070BB":
				self.master_balance_lbl1['fg'] = "#202099"
			self.master_balance_lbl1['fg'] = "#7777FF"
		
		if self.master_balance_lbl1['fg'] != "#00FF00":
			self.master_balance_lbl1.after(25, self.master_green())
	
	def master_red(self):
		
		if self.master_balance_lbl1['fg'] == "#7777FF":
			self.master_balance_lbl1['fg'] = "#7070BB"
		else:
			if self.master_balance_lbl1['fg'] == "#009900":
				self.master_balance_lbl1['fg'] = "#00FF00"
			if self.master_balance_lbl1['fg'] == "#007000":
				self.master_balance_lbl1['fg'] = "#009900"
			if self.master_balance_lbl1['fg'] == "#004000":
				self.master_balance_lbl1['fg'] = "#007000"
			if self.master_balance_lbl1['fg'] == "#101019":
				self.master_balance_lbl1['fg'] = "#004000"	
			if self.master_balance_lbl1['fg'] == "#202099":
				self.master_balance_lbl1['fg'] = "#101019"
			if self.master_balance_lbl1['fg'] == "#7070BB":
				self.master_balance_lbl1['fg'] = "#202099"
			self.master_balance_lbl1['fg'] = "#7777FF"
		
		if self.master_balance_lbl1['fg'] != "#00FF00":
			self.master_balance_lbl1.after(25, self.master_red())
	
	def login_box(self):
	
		#Open window
		self.loginn = Tk()
		self.loginn.title('Login')
		self.loginn.geometry("180x90")
		
		#Create Container
		log = Frame(self.loginn)

		#Username
		lblUsername = LabelFrame(log, text = "Username:", labelanchor = 'w', bd = 0)
		entUsername = Entry(lblUsername, width = 15)
		
		#Password
		lblPassword = LabelFrame(log, text = "Password:", labelanchor = 'w', bd = 0)
		entPassword = Entry(lblPassword, width = 15)
		
		#2-Factor Auth
		lbl2fa = LabelFrame(log, text = "2-FA:", labelanchor = 'w', bd = 0)
		ent2fa = Entry(lbl2fa, width = 5)
		#Send POST request
		btn = Button(log, text = "Login!", fg = "#A1DBCD", bg = "#383A39", command = lambda username = entUsername, password = entPassword, fa2 = ent2fa: self.login(username.get(), password.get(), fa2.get()))
		
		log.pack()
		lblUsername.pack()
		entUsername.pack(side = 'right')
		lblPassword.pack()
		entPassword.pack(side = 'right')
		lbl2fa.pack()
		ent2fa.pack(side = 'right')
		
		btn.pack()
		self.loginn.mainloop()	

	def login(self, username, password, fa2 = ''):
		
		url = 'https://api.primedice.com/api/login'
		post_body = {'username': username, 'password': password, 'opt': fa2}
		
		feedback = self.session_post(url, post_body)
		feedback = feedback.text
		token = feedback.split('access_token":"')[1].split('"')[0]
		tokenF = open("tokens.txt", 'a')
		
		
		tokenF.write(username + ":" + password + " = " + token + "\n")
		print username + ":" + password + ":" + token
		tokenF.close()
		
		
		if self.masterloggedin == False:
			
			#Set the user
			self.mastertoken.append(token)
			self.masterloggedin = True
			self.masteruser['text'] = username
			
			info = json.loads(requests.get("https://api.primedice.com/api/1?access_token=" + token).content)
						
			#For the balance, since PD doesn't use 0.000 and just cuts the trailing. we'll use length method to find out the balance
			self.balance_unchopped = info["user"]["balance"]
			
			if self.balance_unchopped.length() <= 7:
				if self.balance_unchopped.length() == 7:
					self.balance = "0." + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 6:
					self.balance = "0.0" + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 5:
					self.balance = "0.00" + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 4:
					self.balance = "0.000" + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 3:
					self.balance = "0.0000" + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 2:
					self.balance = "0.00000" + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 1:
					self.balance = "0.000000" + str(self.balance_unchopped)
				if self.balance_unchopped.length() == 0:
					self.balance = "0.0000000" + str(self.balance_unchopped)
			else:
				if str(self.balance_unchopped).split("") == 0:
					print 'hi'			
			self.workers.append(token)
			

		
		self.loginn.destroy()
		
	def loss_streak_calc(self):
		about = "Returns Probability of Losing Streak Occuring in Number of Rolls (r).\n\np = probability of winning on a single play\nq = probability of loss on a single play\nr = number of losses in a row\nn = number of plays\n\n\nThe probability of loss streak of length r is: \nq * r(1 + p(n - r))\n\nThis formula requires a probability, expressed as a floating point.\nThe calculator converts your percent odds to that number:\n	49.5% becomes 0.495. \nBy dividing the odds entered by 100 to get p. \nThe odds of loss is calculated from this result by subtracting p from 1.\n\nInstructions:\n\n1. Enter the percent chance of winning in the 'Winning Odds' field. Do NOT enter the '%' sign.\n2. Enter the length of a streak you want to check in the 'treak Length' field.\n3. Enter the number of plays (rolls, spins, buy-ins, etc.) in the 'Game Count' field.\n4. Click the 'Calculate button."
		
		
		#Description Box
		self.descriptionFrame = LabelFrame(self.calc_tab, text = "Description:", bg = "#000000", fg = "#FFFFFF")
		self.descriptionFrame.place(y = 87)
		
		#Description Label
		self.description = Label(self.descriptionFrame, text = about, fg = "#FFFFFF", bg = "#000000", font = ('Arial', 10, 'bold'))
		self.description.pack()
		
		
		#Calculator Box
		self.calc = Frame(self.calc_tab, bd = 2)
		self.calc.pack(side = 'right')
		
		#q = probability of loss on a single play
		self.lblQ = LabelFrame(self.calc, text = "Chance of losing streak:", labelanchor = 'w', bd = 0)
		self.entQ = Entry(self.lblQ, width = 16, bg = "#000000", fg = "#FF0000")
		
		#p = probability of winning on a single play
		self.lblP = LabelFrame(self.calc, text = "Winning chance:", labelanchor = 'w', bd = 0)
		self.entP = ttk.Entry(self.lblP, width = 16)
		
		#r = number of losses in a row
		self.lblR = LabelFrame(self.calc, text = "Streak Langth:", labelanchor = 'w', bd = 0)
		self.entR = ttk.Entry(self.lblR, width = 16)
		
		#n = number of rolls
		self.lblN = LabelFrame(self.calc, text = "Number of rolls:", labelanchor = 'w', bd = 0)
		self.entN = ttk.Entry(self.lblN, width = 16)
		
		
		self.lblQ.pack()
		self.entQ.pack()
		self.lblP.pack()
		self.entP.pack()
		self.lblR.pack()
		self.entR.pack()
		self.lblN.pack()
		self.entN.pack()
		
		#Calculate Button
		self.loss_calc_button = Button(self.calc, width = 10, text = "Calculate!", command = lambda self = self: self.loss_streak_calc_action())
		self.loss_calc_button.pack()
		
	def loss_streak_calc_action(self):
		#Loss streak Calculator
		
		self.p = self.entP.get()
		self.r = self.entR.get()
		self.n = self.entN.get()
		
		L_odds = int(self.p) - 100
		p_odds = int(self.p) / 100
		l_odds = 1 - p_odds
		anwser = (1 + (int(self.n) - int(self.r)) * p_odds) * math.pow(l_odds, int(self.n)) * 100
		
		self.entQ.insert(0, anwser)
		
	def inc_multi_calc():
		print 'hi'


if __name__ == "__main__": 
	q = Queue.Queue()
	app = Main(q)
	





#user = PrimeDice()





#create the widgets for entering a username
#and pack them into to the window
#create a button widget called btn
#pack the widget into the window

#Header
#header = ImageTk.PhotoImage(file = './images/unnamed.png')
#header_image = Label(root, image = header)
#header_image.place(x = 420, y = 230)
