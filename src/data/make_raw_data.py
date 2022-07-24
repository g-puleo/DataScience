#questo script scarica automaticamente i dati necessari per il progetto e li inserisce nella cartella data/raw
#Il link alla pagina dove sono disponibili è https://dataverse.harvard.edu/dataverse/bigdatachallenge
import requests
import os

def downloadData(fname, url, folder='data/raw'):
	response = requests.get(url)
	name = "../../"+ folder + "/" + fname 
	filename = os.path.join( os.path.dirname(__file__), name)
	with open(filename, "wb") as f:
		f.write(response.content)
		print(f"file {fname} salvato con successo in\n {filename}\n")


URL_trentinogrid="https://dvn-cloud.s3.amazonaws.com/10.7910/DVN/FZRVSX/14d33123790-ddf0441792be?response-content-disposition=attachment; filename*=UTF-8''trentino-grid.geojson&response-content-type=text/plain; charset=US-ASCII&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220724T184423Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=AKIAIEJ3NV7UYCSRJC7A/20220724/us-east-1/s3/aws4_request&X-Amz-Signature=08a43cf0c72b65e0e7ad5d4250686c123943c274e029bf3f42300d18c99b3977"
downloadData('trentino-grid.geojson', URL_trentinogrid)

URL_meteotrentino = "https://dvn-cloud.s3.amazonaws.com/10.7910/DVN/UPODNL/14d33164ea6-882218bb6c05?response-content-disposition=attachment; filename*=UTF-8''meteotrentino-weather-station-data.json&response-content-type=text/plain; charset=US-ASCII&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220724T185859Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=AKIAIEJ3NV7UYCSRJC7A/20220724/us-east-1/s3/aws4_request&X-Amz-Signature=37f0f50bce8c66a9643020b5d44304fb7b982fb80684509d5df9cd80f971417e"
downloadData('meteotrentino-weather-station-data.json', URL_meteotrentino)

URL_LINE = "https://dvn-cloud.s3.amazonaws.com/10.7910/DVN/AMKZXM/14d3317e9c0-a67f75cdd669?response-content-disposition=attachment; filename*=UTF-8''line.csv&response-content-type=text/plain; charset=US-ASCII&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220724T191620Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=AKIAIEJ3NV7UYCSRJC7A/20220724/us-east-1/s3/aws4_request&X-Amz-Signature=88f47d7352c73b7118dbb377459bf3404a68323eee1b78b1512f12300a843917"
downloadData('line.csv', URL_LINE)

URL_DEC = "https://dvn-cloud.s3.amazonaws.com/10.7910/DVN/AMKZXM/14d3317fbc2-066503ae4c2e?response-content-disposition=attachment; filename*=UTF-8''SET-dec-2013.csv&response-content-type=text/plain; charset=US-ASCII&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220724T191832Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=AKIAIEJ3NV7UYCSRJC7A/20220724/us-east-1/s3/aws4_request&X-Amz-Signature=5178fafd17c8be8a0013de61a6b2ba38bfa1fc529bd00eb62757df4e1211f91a"
downloadData("SET-dec-2013.csv", URL_DEC)

URL_NOV = "https://dvn-cloud.s3.amazonaws.com/10.7910/DVN/AMKZXM/14d33181012-6906e37f0157?response-content-disposition=attachment; filename*=UTF-8''SET-nov-2013.csv&response-content-type=text/plain; charset=US-ASCII&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220724T201251Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=AKIAIEJ3NV7UYCSRJC7A/20220724/us-east-1/s3/aws4_request&X-Amz-Signature=6c401ffe8429a868650191c2fcb23fa980e2395217728e2da6c21b9620eb08c2"
downloadData("SET-nov-2013.csv", URL_DEC)

print("Dati raw importati correttamente da Harvard Dataverse!")
