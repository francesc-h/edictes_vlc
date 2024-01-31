# Publicació automatitzada d'edictes d'informació pública de l'Ajuntament de València

L'accés efectiu a la informació pública de les administracions és fonamental per a una participació ciutadana útil i transformadora. Mitjançant aquesta ferramenta es publiquen automatitzadament els edictes d'informació pública de l'Ajuntament de València en [aquest compte de Twitter](https://twitter.com/edictes_vlc).

L'objectiu d'aquesta ferramenta és facilitar a la ciutadania l'accés a aquests documents, ja que, fins ara, resulta tediós i poc àgil haver d'estar consultant diàriament [el web de l'Ajuntament](https://sede.valencia.es/sede/edictos/index/materia/LA) per mantindre's al dia de nous projectes. Emprar Twitter resulta més còmode, ja que és una xarxa social que moltes persones ja utilitzem en el nostre dia a dia i a més, en seguir un compte, permet activar notificacions, de manera que quan el bot detecte un nou edicte pots ser informat de manera proactiva.

El programari que fa possible aquesta ferramenta és el següent:
- El bot es troba allotjat al núvol d'Azure, específicament mitjançant [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview?pivots=programming-language-python) i la base de dades [Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction) per mantindre un registre de tots els edictes processats.
- Donat que el web de l'Ajuntament és estàtic, la  recol·lecció de dades s'aconseguix simplement utilitzant [requests](https://requests.readthedocs.io/en/latest/) i [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
- L'extracció de la informació als PDFs es realitza amb [PyMuPDF](https://pymupdf.readthedocs.io/en/la.test/module.html)
- La publicació a Twitter es du a terme gràcies a [tweepy](https://www.tweepy.org/).