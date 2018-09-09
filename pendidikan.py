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
	'id_lembaga': ''
}

url_user = {
	'admin' : '',
	'biktren-putra' : 'biktren-putra/',
	'biktren-putri' : 'bintren-putri/',
	'lembaga' : ''
}

def update():
	pedatren = open('pedatren.txt','a')
	headers = {
		'x-token':token,
		'content-type': 'application/json'
	}
	data = requests.get(url+'{}pelajar?page=1&limit=1'.format(setting['url']), headers=headers)
	content = json.loads(data.content)
	setting['id_lembaga'] = content[0]['pendidikan']['id_lembaga']

	sql = 'select * from mtsnj where kelas="IX"'
	cur.execute(sql)
	hasil = cur.fetchall()
	print("id Lembaga : "+setting['id_lembaga'])
	for a in hasil:
		try:
			data = requests.get(url+'person/{}'.format(a[0]), headers=headers)
			i = json.loads(data.content)
			num = 0
			cek = len(i['pendidikan'])
			for b in range(cek):
				if i['pendidikan'][num]['id_lembaga'] == setting['id_lembaga'] :
					payload = {
						'nomor_induk':'%s'%a[3],
						'id_lembaga':'%s'%i['pendidikan'][num]['id_lembaga'],
						'tanggal_mulai':'%s'%i['pendidikan'][num]['tanggal_mulai']
					}
					a = ("\nSedang Meng Update Nomor Induk Nanda : "+i['nama_lengkap']+"\n")
					pedatren.write(a)
					data = requests.put(url+'person/{}/pendidikan/{}'.format(i['uuid'],i['pendidikan'][num]['id']), data=json.dumps(payload), headers=headers)
					b = (str(data.content))
					pedatren.write(b)
					pedatren.write("\n")
					print(a)
					print(b)
				num += 1
		except Exception, e:
			a = ("Ada Error UUID : "+a[0], e)
			pedatren.write(str(a))
			pedatren.write("\n")
			print(a)
	
	pesan = raw_input("\n\nLog out ?  (Y/T) : ")
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
	else:
		print("Username atau Password Salah :(")
		sys.exit()

def cek_login(url):
	data = requests.get(url+'auth/login', headers={'x-token':token})
	if data.status_code == 401 or data.status_code == 403:
		print("Proses Login Ulang")
		login(url)
		user_cek()
	elif data.status_code == 200:
		print("Sudah Login :)")
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
		if 'lembaga' in i:
			b = user_level.split("-")[1]
			setting['url'] = "lembaga/{}/".format(b)
		elif user_level in i:
			a = url_user[user_level]
			setting['url'] = a

def logout(url):
	pesan = raw_input("Yakin Mau Logout ? (Y/T) : ")
	if pesan.lower() == 'y':
		data = requests.get(url+'auth/logout', headers={'x-token':token})
		if data.status_code == 200:
			print(data.text+"\nLog Out Berhasil")

if cek_login(url) == 200:
	update()
