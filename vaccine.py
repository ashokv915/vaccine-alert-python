import requests
from datetime import datetime
import json
import time

base_cowin_url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
reg_link = "https://selfregistration.cowin.gov.in/"
now = datetime.now()
today_date = now.strftime("%d-%m-%Y")
import datetime
tomorrow_date = (now + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
day_after_tomorrow = (now + datetime.timedelta(days=2)).strftime("%d-%m-%Y")
api_url_telegram = "https://api.telegram.org/<KEY>/sendMessage?chat_id=@__groupid__&text="
group_id = "<GRP_NAME>"
nearest_pincodes = [679313, 679307, 679503, 679308, 679303, 679309, 679102, 679121,679322,679551]

# center_dict ={
# 	111570: 0,
# 	110343:0,
# 	704419:0,
# 	111043:0,
# 	705160:0,
# 	110756:0,
# 	704446:0,
# 	703717:0,
# 	705164:0,
# 	704449:0,
# 	111076:0
# }

def fetch_data_from_cowin(district_id,dates):
	logging.debug("In fetch_data_from_cowin function")
	query_params = "?district_id={}&date={}".format(district_id,dates)
	logging.debug(query_params)
	header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	final_url = base_cowin_url + query_params
	logging.debug(final_url)
	try:
		response = requests.get(final_url)
		logging.info(response)
		extract_availability_data(response)
	except Exception as e:
		logging.error("Could not connect to the url: {} Error: {}".format(final_url,e))
	#print(response.text)

def extract_availability_data(response):
	respose_json = response.json()
	logging.debug("Response converted into json")
	for center in respose_json["sessions"]:
		logging.debug("Center Name: {} CenterID: {}".format(center["name"],center["center_id"]))
		if center["available_capacity"] >= 0:  
			center_dict_dose1.setdefault(str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"]),0)
			center_dict_dose2.setdefault(str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"]),0)
			logging.info(" Date:{} Dose1:{} Dose2:{} Place:{} CenterID:{}".format(center["date"],center["available_capacity_dose1"],center["available_capacity_dose2"],center["name"],center["center_id"]))
			if (center["available_capacity"] > 0) or (center_dict_dose1[str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"])] > 0) or (center_dict_dose2[str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"])] > 0):
				if center["pincode"] in nearest_pincodes:
					logging.info("Pincode matched: ")
					logging.debug(str(center["pincode"]))
					past_count_dose1 = center_dict_dose1[str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"])]
					past_count_dose2 = center_dict_dose2[str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"])]
					present_count_dose1 = center["available_capacity_dose1"]
					present_count_dose2 = center["available_capacity_dose2"]
					logging.debug("PastCountDose1: {} PresentCountDose1: {} PastCountDose2: {} PresentCountDose2: {}".format(past_count_dose1,present_count_dose1,past_count_dose2,present_count_dose2))
					if (present_count_dose1 != past_count_dose1) or (present_count_dose2 != past_count_dose2):
						center_dict_dose1[str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"])] = center["available_capacity_dose1"]
						center_dict_dose2[str(center["center_id"])+"_"+center["date"]+"_"+str(center["min_age_limit"])] = center["available_capacity_dose2"]
						logging.info("Slots updated")
						message = " Date: {0} \nPlace: {1} \nDose1: {2} \nDose2: {3} \nMinimum Age: {4} \nVaccine:{5} \nCost: {6} \nPincode: {7} \n \n \n {8}".format(center["date"], center["name"], center["available_capacity_dose1"], center["available_capacity_dose2"], center["min_age_limit"],center["vaccine"],center["fee_type"],center["pincode"],reg_link)
						send_message_telegram(message)
						logging.debug("Message sent successfully: ")
						print(center["center_id"], center["name"], center["available_capacity_dose1"], center["min_age_limit"])
						with open('district_count_dose1.json', 'w') as cred:
							json.dump(center_dict_dose1, cred)
						with open('district_count_dose2.json', 'w') as cred:
							json.dump(center_dict_dose2, cred)

def send_message_telegram(message):
	logging.info("Message sent from send Message function")
	final_telegram_url = api_url_telegram.replace("__groupid__", group_id)
	final_telegram_url = final_telegram_url+message
	response = requests.get(final_telegram_url)

# def second_dose_alert(present2, past2,message,center_dict_dose2):
# 	if (present2) <= (past2-10):
# 		send_message_telegram(message)
# 		with open('district_count_dose2.json', 'w') as cred:
# 			json.dump(center_dict_dose2, cred)
# 		logging.debug("Dose2 Message sent successfully")


if __name__ == "__main__":
	#send_message_telegram("maintenance Break, Restart Soon!")
	import logging
	logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s - %(message)s')
	with open('district_count_dose1.json', 'r') as json_file:
		center_dict_dose1 = json.load(json_file)
	with open('district_count_dose2.json', 'r') as json_file:
		center_dict_dose2 = json.load(json_file)
	while True:
		#fetch_data_from_cowin(308,today_date)
		#fetch_data_from_cowin(302,today_date)
		#time.sleep(20)
		fetch_data_from_cowin(308,tomorrow_date)
		fetch_data_from_cowin(302,tomorrow_date)
		time.sleep(20)
		fetch_data_from_cowin(308,day_after_tomorrow)
		time.sleep(5)
