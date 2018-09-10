import MySQLdb, requests, json, sys, base64
from requests.auth import HTTPBasicAuth
from getpass import getpass

conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='pedatren')
cur = conn.cursor()

url = 'https://api.pedatren.nuruljadid.app/'

with open('token.txt', 'r') as peda:
	token = peda.read()
setting = {
	'url':'',
	'level':'',
	'token':token,
	'id_lembaga': '',
	'status': ''
}

url_user = {
	'admin' : '',
	'biktren-putra' : 'biktren-putra/',
	'biktren-putri' : 'bintren-putri/',
	'lembaga' : '',
	'wilayah': '',
	'mahrom':''
}
params = {
	'page':'1',
	'limit':'5',
	'sortby': 'kelas_lembaga.id'
}

def insert():	
	if setting['status'] == 'admin':
		params.__setitem__('lembaga', '{}'.format(setting['id_lembaga']))
	print("ID Lembaga : "+setting['id_lembaga'])
	print("Lembaga ID : "+str(params['lembaga']))
	data = requests.get(url+'{}pelajar'.format(setting['url']), headers={'x-token':token}, params=params)
	content = json.loads(data.content)
	for i in content:
		sql = 'select uuid from induk where uuid="{}"'.format(i['uuid'])
		cur.execute(sql)
		if cur.fetchone() > 0:
			print("Sudah Ada : ")
		else:
			sql = 'insert into induk (uuid, nama_lengkap, kelas, jurusan) values ("{}","{}","{}","{}")'\
			.format(i['uuid'],i['nama_lengkap'],str(i['pendidikan']['kelas']),str(i['pendidikan']['jurusan']))
			cur.execute(sql)
			conn.commit()
			print("Berhasil Nambah : "+i['nama_lengkap'])
	a = raw_input("Mau Log Out ? (Y/T) : ")
	if a.lower() == 'y':
		logout(url)

def update():
	pedatren = open('pedatren.txt','a')
	headers = {
		'x-token':token,
		'content-type': 'application/json'
	}
	sql = 'select uuid, nomor_induk from induk where kelas="vii" and nomor_induk is not null'
	cur.execute(sql)
	hasil = cur.fetchall()
	for a in hasil:		
		try:
			data = requests.get(url+'person/{}'.format(a[0]), headers=headers)
			i = json.loads(data.content)
			num = 0
			cek = len(i['pendidikan'])
			for b in range(cek):
				if i['pendidikan'][num]['id_lembaga'] == setting['id_lembaga'] :
					payload = {
						'nomor_induk':'%s'%a[1],
						'id_lembaga':'%s'%i['pendidikan'][num]['id_lembaga'],
						'tanggal_mulai':'%s'%i['pendidikan'][num]['tanggal_mulai']
					}					
					data = requests.put(url+'person/{}/pendidikan/{}'.format(i['uuid'],\
						i['pendidikan'][num]['id']), data=json.dumps(payload), headers=headers)
					a = ("Sedang Meng Update Nomor Induk Nanda : "+i['nama_lengkap'])
					pedatren.write(a)
					pedatren.write("\n")
					b = (str(data.text)+"\n\n")
					if data.status_code == 200:
						b = (str(b))
						pedatren.write(b)
						print(a)
						print(b)
					else:											
						pedatren.write("Nomor Induk Ada Yang Sama dengan lembaga lain :(\n")
						pedatren.write(b)
						print(a)
						print(b)
				num += 1
		except Exception, e:
			a = ("Ada Error UUID : "+str(a[0]), e)
			pedatren.write(str(a))
			pedatren.write("\n")
			print(a)
	
	pesan = raw_input("\nLog out ?  (Y/T) : ")
	if pesan.lower() == 'y':
		logout(url)	

def login(url):
	user = raw_input('Masukkan Username : ')
	password = getpass('Masukkan Password : ')
	tok = open('token.txt', 'w')
	data = requests.get(url+'auth/login', auth=HTTPBasicAuth(user,password))
	if data.status_code == 200:
		token = data.headers['x-token']
		tok.write(token)
		tok.close()
		setting['token'] = token
		print(data.content)
		print("Silahkan Ulangi :)")
	else:
		print("Username atau Password Salah :(")
		sys.exit()

def cek_login(url):
	data = requests.get(url+'auth/login', headers={'x-token':token})
	if data.status_code == 401 or data.status_code == 403:
		print("Proses Login Ulang")
		login(url)
	user_cek()
	return data.status_code

def decode_base64(data):	
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'='* (4 - missing_padding)
    return base64.decodestring(data)

def user_cek():
	user = setting['token'].split(".")[0]
	user_level = json.loads(decode_base64(user))['scope'][0]
	setting['level'] = user_level
	for i in url_user:
		if 'lembaga' in user_level:
			b = user_level.split("-")[1]
			setting['url'] = "lembaga/{}/".format(b)
		elif user_level in i:
			a = url_user[user_level]
			setting['url'] = a
			setting['status'] = 'admin'

def logout(url):
	pesan = raw_input("Yakin Mau Logout ? (Y/T) : ")
	if pesan.lower() == 'y':
		data = requests.get(url+'auth/logout', headers={'x-token':token})
		if data.status_code == 200:
			print(data.text+"\nLog Out Berhasil")

def setting_lembaga():
	data = requests.get(url+'setting/lembaga', headers={'x-token':token})
	content = json.loads(data.content)
	num = 1
	for i in content:
		print("{}  ".format(num)+i['nama'])
		setting.__setitem__('{}'.format(num),'{}'.format(i['id']))
		num += 1

if cek_login(url) == 200:
	setting_lembaga()
	a = raw_input("\nMasukkan Pilihan : ")
	if a in setting:
		setting['id_lembaga'] = setting[a]
		print '''
		1. Ambil Data Pedatren, simpan ke database
		2. Update Nomor Induk'''
		a = raw_input("\nSilahkan Masukkan Pilihan : ")
		if a == '1':
			insert()
		elif a == '2':			
			update()
		else:
			print("Sing genna loh mas")
	else:
		print("Sing Genna Loh Mas:(")