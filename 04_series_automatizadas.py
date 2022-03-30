import os
import pyfiglet
import termcolor
from unidecode import unidecode
import requests
import json
import time
from imdb import IMDb
from datetime import datetime, timedelta
from twilio.rest import Client
import pandas as pd
from bs4 import BeautifulSoup
import tmdbsimple as tmdb

search = tmdb.Search()
ia = IMDb()

print('teste2')

tmdb.API_KEY = '31d8c5dee3141d702e6d6c1f4a110d5f'
os.system('cls' if os.name == 'nt' else 'clear')

account_sid = "AC7ceca3319de32ab578ca4b3f8418066d"
auth_sid = "1186a126588306f1d9d4b91806e9fbd6"
client = Client(account_sid, auth_sid)

print(pyfiglet.figlet_format('STREAMFILMES'))
print(' ', end='\r\t\t\t\t\t\t\t')
print(termcolor.colored(color='yellow', text='By: Mateuslapa'))

### LÊ O ARQUIVO ANTEIROR
with open("arquivoNomes.txt", "r") as arquivoNome:
    nomesArquivo = arquivoNome.readlines()

### CRIA UM ARQUIVO DA ATUALIZAÇÃO DAS SÉRIES
arquivo = open("seriesAtualizadas.txt", "a")

### CRIA UM ARQUIVO COM PROBLEMAS NAS SÉRIES
arquivoErros = open("seriesErros.txt", "r")
seriesErros = arquivoErros.readlines()

url_serie = 'https://vizer.tv/'
data = requests.get(url_serie).text
soup = BeautifulSoup(data, 'html.parser')
divNovosEpisodios = soup.find('div', id='homeSliderSerieList')
nomeNovosEpisodios = divNovosEpisodios.findAll('span')

valida_serie = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder=VPsJCu4Q8vU'
page_valida = requests.get(valida_serie)
soup_valida = BeautifulSoup(page_valida.content, 'html.parser')

# Collecting Ddata
for epPep in nomeNovosEpisodios:      
    
    ## PROCURA PELO IMDB
    buscaIMDB = ia.search_movie('{}'.format(str(epPep.text)))
    if len(buscaIMDB) == 0:
        ## VERIFICA SE A SÉRIE JÁ ESTA NO ARQUIVO DE ERRO
        encontrouErro = 0
        for searchErro in seriesErros:
            if searchErro == epPep.text:
                encontrouErro = 1
        
        if encontrouErro == 1:
            continue
        else:
            seriesErros.append('\n' + str(epPep.text))
            client.messages.create(
                from_="+13155099696",
                body="Erro! A série: {} não foi encontrada no IMDB".format(str(epPep.text)),
                to="+5548998062066"
            )
            continue

    titulo = epPep.text
    imdb_serie = 'tt' + str(buscaIMDB[0].movieID)
    url_banner = 'https://streamfilmes.com/api/img/banner_player.jpg'

    tituloFormatado = unidecode(titulo.replace(" ", "").lower())
    nome_serie = ''.join(filter(str.isalnum, tituloFormatado)) 

    arquivo.write("\nSerie: " + str(titulo))
    response = search.tv(query="{}".format(str(titulo)))

    for s in search.results:
        tmdb_serie = s['id']
    
    print('\n')
    print('Analisando episódios da serie...', end='\r\t\t\t\t\t')
    print(termcolor.colored(color='green', text='[{}]'.format(str(nome_serie))))
    print('IMDB da serie...', end='\r\t\t\t\t\t')
    print(termcolor.colored(color='green', text='[{}]'.format(str(imdb_serie))))
    time.sleep(30)

    ## VERIFICA SE JÁ EXISTE A SÉRIE CADASTRADA NO STREAMTAPE
    ###########################################################################
    for procuraSerie in soup_valida:
        valida = json.loads(procuraSerie)

        todasSeries1 = ''
        for k, v in valida.items():
            if(k == 'result'):
                todasSeries1 = v['folders']

    encontrou = 0
    for serie in todasSeries1:
        if(serie['name'] == nome_serie):
            encontrou = 1
            idSerieEncontrada = serie['id']

    if(encontrou == 0):
        print('\n')
        print(termcolor.colored(color='red', text='Essa série não está cadastrada no Streamtape!'))
        print('--> Iniciando o processo de cadastro no Streamtape...')
        print(termcolor.colored(color='blue', text='--> Iniciando o processo de busca no WAREZCDN...'))

        idPlayer = 0
        url_serie = 'https://embed.warezcdn.net/serie/'+str(imdb_serie)

        page = requests.get(url_serie)
        soup = BeautifulSoup(page.content, 'html.parser')

        ### RESULTADOS
        _resultadoTemporada1 = 'div[class="item active"]'
        _resultadoTemporadas = 'div[class="item"]'

        ### ELEMENTOS
        job_temps1 = soup.select(_resultadoTemporada1)
        job_temps_resto = soup.select(_resultadoTemporadas)

        ### VERIFICA O TOTAL DE TEMPORADAS
        ids_temps = {}
        for temporadas in job_temps1:
            ids_temps[temporadas.text] = temporadas.attrs.get("data-load-episodes")

        for temporadas in job_temps_resto:
            if(temporadas.attrs.get("data-load-episodes")):
                ids_temps[temporadas.text] = temporadas.attrs.get("data-load-episodes")

        print('\n')
        print("Temporadas: " + str(termcolor.colored(color='green', text='{}'.format(str(len(ids_temps))))))
        print("id: " + str(termcolor.colored(color='green', text='{}'.format(str(imdb_serie)))))
        print('\n')

        print('Criando pasta da série...', end='\r\t\t\t\t\t')
        url_pasta = 'https://api.streamtape.com/file/createfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&name={}&pid=VPsJCu4Q8vU'.format(str(nome_serie))
        page_pasta = requests.get(url_pasta)
        soup_page_pasta = BeautifulSoup(page_pasta.content, 'html.parser')
        print(termcolor.colored(color='green', text='[OK]'))

        for buscaPasta in soup_page_pasta:
            pasta = json.loads(buscaPasta)

            for k, v in pasta.items():
                if(k == 'result'):
                    idPasta = v['folderid']

        print('Criando pasta da(s) temporada(s)...', end='\r\t\t\t\t\t')
        ids_pasta_temporadas = {}
        for percorre_temporadas in range(len(ids_temps)):
            cria_pasta_temporada = 'https://api.streamtape.com/file/createfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&name=T{}&pid={}'.format(str(percorre_temporadas+1), str(idPasta))
            page_cria_pasta= requests.get(cria_pasta_temporada)
            soup_cria_pasta = BeautifulSoup(page_cria_pasta.content, 'html.parser')

            for pasta_criada in soup_cria_pasta:
                pasta_temporada = json.loads(pasta_criada)

                for k, v in pasta_temporada.items():
                    if(k == 'result'):
                        ids_pasta_temporadas['T{}'.format(str(percorre_temporadas+1))] = v['folderid']

        print(termcolor.colored(color='green', text='[OK]'))
        print('\n')

        leg_eps = {}
        ### PERCORRE AS TEMPORADAS:
        for temporada in range(len(ids_temps)):
            print("---> Temporada: " + str(temporada+1))
            arg_temporada = temporada+1

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'authority': 'embed.warezcdn.net'
            }

            data = {
                'getEpisodes': ids_temps['{}'.format(arg_temporada)]
            }

            #print('getEpisodes: ' + str(ids_temps['{}'.format(arg_temporada)]))

            page_episodios = requests.post('https://embed.warezcdn.net/serieAjax.php', data=data, headers=headers)
            episodios = BeautifulSoup(page_episodios.content, 'html.parser')
            
            for totalEpisodios in episodios:
                tEpi = json.loads(totalEpisodios)
            
            for k, v in tEpi.items():
                if(k == 'count'):
                    totalizadoEpisodios = v

            print('--> Episódios: ' + str(len(v)))

            contadorEpisodios = 1
            for percorre in episodios:
                value = json.loads(percorre)

                for k, v in value.items():
                    if(k == 'list'):
                        todosEpisodios = v
                
                for EpPorEp, conteudo in todosEpisodios.items():
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'authority': 'embed.warezcdn.net'
                    }

                    data = {
                        'getAudios': conteudo['id']
                    }

                    page_video = requests.post('https://embed.warezcdn.net/serieAjax.php', data=data, headers=headers)
                    players = BeautifulSoup(page_video.content, 'html.parser')

                    for video in players:
                        valueVideo = json.loads(video)
                    
                        for m, n in valueVideo.items():
                            if(m == 'list'):
                                todosVideos = n
                        
                        for playerPorPlayer, conteudoVideo in todosVideos.items():
                            if(len(todosVideos) == 2):
                                if(conteudoVideo['audio'] == '2'):
                                    idPlayer = conteudoVideo['id']
                            else:
                                if(conteudoVideo['audio'] == '2'):
                                    idPlayer = conteudoVideo['id']
                                else:
                                    idPlayer = conteudoVideo['id']

                    url_final = requests.get('https://embed.warezcdn.net/getPlay.php?id={}&sv=streamtape'.format(str(idPlayer)))
                    player_final = BeautifulSoup(url_final.content, 'html.parser')

                    data = player_final.find('script')

                    teste = data.text
                    teste = teste.replace('"', '').replace(';', '')
                    tamanho_link = len(teste)
                    posicao_link = teste.find('https')
                    legenda_link = teste.find('&c1_file=')

                    if(contadorEpisodios < 10):
                        nEpisodio = '0{}'.format(str(contadorEpisodios))
                    else :
                        nEpisodio = contadorEpisodios

                    ## Verifica Legenda
                    if legenda_link == -1:
                        link_final = teste[posicao_link:tamanho_link-2]
                    else:
                        leg_eps['{}x{}'.format(str(arg_temporada), str(contadorEpisodios))] = teste[legenda_link+9:tamanho_link-21]
                        link_final = teste[posicao_link:]

                    nameArquivo = str(nome_serie) + str(arg_temporada) + 'x' + str(nEpisodio)
                    ## Aqui faz o envio do video para a pasta da série
                    url_pasta = 'https://api.streamtape.com/remotedl/add?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&url={}&folder={}&name={}'.format(str(link_final), str(ids_pasta_temporadas['T{}'.format(temporada+1)]), str(nameArquivo))
                    page_pasta = requests.get(url_pasta)
                    print("Episódio " + str(contadorEpisodios) + " - " + str(link_final))
                    contadorEpisodios = contadorEpisodios + 1

            print('\n')
            print('\n')

        print(termcolor.colored(color='blue', text='--> Iniciando o processo de cadastro na API StreamFilmes...'))
        print('\n')

        busca_serie = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder=VPsJCu4Q8vU'
        page_busca = requests.get(busca_serie)
        soup_busca = BeautifulSoup(page_busca.content, 'html.parser')
        for buscaSerie in soup_busca:
            serie = json.loads(buscaSerie)

            todasSeries2 = ''
            for k, v in serie.items():
                if(k == 'result'):
                    todasSeries2 = v['folders']

        encontrou = 0
        for serie in todasSeries2:
            if(serie['name'] == nome_serie):
                idPastaSerie = serie['id']
                encontrou = 1

        if(encontrou == 0):
            print(termcolor.colored(color='red', text='Série não encontrada!'))
            exit()

        url_serie_streamtape = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder={}'.format(str(idPastaSerie))
        page_streamtape = requests.get(url_serie_streamtape)
        soup_streamtape = BeautifulSoup(page_streamtape.content, 'html.parser')

        print("Entrando na pasta...")
        print('\n')

        for temporadasStreamtape in soup_streamtape:
            vArq = json.loads(temporadasStreamtape)

            for k, v in vArq.items():
                if(k == 'result'):
                    totalTemporadas = len(v['folders'])
                    todasPastas = v['folders']
                    print("Temporadas: " + str(termcolor.colored(color='green', text='{}'.format(str(totalTemporadas)))))
                    print('\n')

        for tempPtemp in range(len(v['folders'])):
            print('--> Iniciando Temporada ' + str(tempPtemp+1))

            for temporada in todasPastas:
                if(temporada['name'] == 'T{}'.format(str(tempPtemp+1))):
                    idTemporada = temporada['id']

                    url_temporada = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder={}'.format(str(idTemporada))
                    page_temporada = requests.get(url_temporada)
                    retorno_temporada = BeautifulSoup(page_temporada.content, 'html.parser')

                    for epTemporadas in retorno_temporada:
                        vEpTemp = json.loads(epTemporadas)

                        for k, v in vEpTemp.items():
                            if(k == 'result'):
                                totalEpisodios = len(v['files'])
                                todosEpisodios = v['files']
                                print('Episódios: ' + str(totalEpisodios))

                                contadorEpisodios = 1
                                for teste in todosEpisodios:
                                    link_episodio = str(teste['link'].replace('/v/', '/e/'))

                                    link_da_legenda = ''
                                    encontrou_legenda = 0
                                    for pLeg in leg_eps:
                                        if pLeg == '{}x{}'.format(str(tempPtemp+1), str(contadorEpisodios)):
                                            encontrou_legenda = 1

                                    if encontrou_legenda == 1:
                                        link_da_legenda = leg_eps['{}x{}'.format(str(tempPtemp+1), str(contadorEpisodios))]

                                    url_streamfilmes = 'https://streamfilmes.com/api/req_series.php?nome={}&imagen={}&titulo=DUBLADO&link={}&imdb={}&temporada={}&episodio={}&legenda={}'.format(str(nome_serie), str(url_banner), str(link_episodio), str(tmdb_serie), str(tempPtemp+1), str(contadorEpisodios), str(link_da_legenda))
                                    page_streamfilmes = requests.get(url_streamfilmes)
                                    print('Episódio: ' + str(contadorEpisodios) + ' - ' + str(link_episodio))
                                    contadorEpisodios = contadorEpisodios + 1
        client.messages.create(
            from_="+13155099696",
            body="Série: {} adicionada ao Streamtape!".format(str(titulo)),
            to="+5548998062066"
        )
        continue
    
    ## VERIFICA O WAREZ
    ###########################################################################
    print(termcolor.colored(color='blue', text='--> Iniciando o processo de busca no Warezcdn...'))

    idPlayer = 0
    url_serie = 'https://embed.warezcdn.net/serie/'+str(imdb_serie)

    page = requests.get(url_serie)
    soup = BeautifulSoup(page.content, 'html.parser')

    ### RESULTADOS
    _resultadoTemporada1 = 'div[class="item active"]'
    _resultadoTemporadas = 'div[class="item"]'

    ### ELEMENTOS
    job_temps1 = soup.select(_resultadoTemporada1)
    job_temps_resto = soup.select(_resultadoTemporadas)

    ### VERIFICA O TOTAL DE TEMPORADAS
    ids_temps = {}
    for temporadas in job_temps1:
        ids_temps[temporadas.text] = temporadas.attrs.get("data-load-episodes")

    for temporadas in job_temps_resto:
        if(temporadas.attrs.get("data-load-episodes")):
            ids_temps[temporadas.text] = temporadas.attrs.get("data-load-episodes")

    print("Temporadas: " + str(termcolor.colored(color='green', text='{}'.format(str(len(ids_temps))))))
    print('\n')

    if len(ids_temps) == 0:
        encontrouErro = 0
        for searchErro in seriesErros:
            if searchErro == titulo:
                encontrouErro = 1
        
        if encontrouErro == 1:
            continue
        else:
            seriesErros.append('\n' + str(titulo))
            client.messages.create(
                from_="+13155099696",
                body="Erro! Não foi possível atualizar/cadastrar a serie: {}".format(str(titulo)),
                to="+5548998062066"
            )
                

        continue


    ## VERIFICA O STREAMTAPE
    ###########################################################################
    print(termcolor.colored(color='blue', text='--> Iniciando o processo de busca no Streamtape...'))

    busca_serie = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder=VPsJCu4Q8vU'
    page_busca = requests.get(busca_serie)
    soup_busca = BeautifulSoup(page_busca.content, 'html.parser')
    for buscaSerie in soup_busca:
        serie = json.loads(buscaSerie)

        todasSeries3 = ''
        for k, v in serie.items():
            if(k == 'result'):
                todasSeries3 = v['folders']

    encontrou = 0
    for serie in todasSeries3:
        if(serie['name'] == nome_serie):
            idPastaSerie = serie['id']
            encontrou = 1

    if(encontrou == 0):
        print('\n')
        print(termcolor.colored(color='red', text='Série não encontrada!'))
        exit()

    url_serie = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder={}'.format(str(idPastaSerie))
    page = requests.get(url_serie)
    soup = BeautifulSoup(page.content, 'html.parser')

    for temporadas in soup:
        vArq = json.loads(temporadas)

        for k, v in vArq.items():
            if(k == 'result'):
                totalTemporadas = len(v['folders'])
                todasPastas = v['folders']
                print("Temporadas: " + str(termcolor.colored(color='green', text='{}'.format(str(totalTemporadas)))))
                print('\n')

    ## COMPARA A QUANTIDADE DE TEMPORADAS ENTRE O STREAMTAPE E O WAREZ
    print('Comparação de temporadas: ', end='\r\t\t\t\t\t')
    if(totalTemporadas != len(ids_temps)):
        print(termcolor.colored(color='yellow', text='[DIFERENTE]'))

        if(totalTemporadas > len(ids_temps)):
            print(termcolor.colored(color='red', text='Streamtape tem mais temporadas que o warez!'))
            continue
        else:
            ## INICIA O PROCESSO DE CRIAÇÃO DA PASTA DA TEMPORADA
            print('Criando pasta da(s) temporada(s)...', end='\r\t\t\t\t\t')
            diferencaTemporadas = (len(ids_temps) - totalTemporadas)
            ids_pasta_temporadas = {}
            for percorre_temporadas in range(len(ids_temps)):
                if(percorre_temporadas+1 > totalTemporadas):
                    cria_pasta_temporada = 'https://api.streamtape.com/file/createfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&name=T{}&pid={}'.format(str(percorre_temporadas+1), str(idSerieEncontrada))
                    page_cria_pasta= requests.get(cria_pasta_temporada)
                    soup_cria_pasta = BeautifulSoup(page_cria_pasta.content, 'html.parser')

                    for pasta_criada in soup_cria_pasta:
                        pasta_temporada = json.loads(pasta_criada)

                        for k, v in pasta_temporada.items():
                            if(k == 'result'):
                                ids_pasta_temporadas['T{}'.format(str(percorre_temporadas+1))] = v['folderid']

            print(termcolor.colored(color='green', text='[OK]'))
            print('Diferença: ', end='\r\t\t\t\t\t')
            print(termcolor.colored(color='yellow', text='{}'.format(str(diferencaTemporadas))))
            print('\n')

            leg_eps = {}
            for temporada in range(len(ids_temps)):
                if(temporada+1 > totalTemporadas):
                    print("---> Temporada: " + str(temporada+1))
                    arg_temporada = temporada+1

                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'authority': 'embed.warezcdn.net'
                    }

                    data = {
                        'getEpisodes': ids_temps['{}'.format(arg_temporada)]
                    }

                    page_episodios = requests.post('https://embed.warezcdn.net/serieAjax.php', data=data, headers=headers)
                    episodios = BeautifulSoup(page_episodios.content, 'html.parser')
                    
                    for totalEpisodios in episodios:
                        tEpi = json.loads(totalEpisodios)
                    
                    for k, v in tEpi.items():
                        if(k == 'count'):
                            totalizadoEpisodios = v

                    print('--> Episódios: ' + str(len(v)))

                    contadorEpisodios = 1
                    for percorre in episodios:
                        value = json.loads(percorre)

                        for k, v in value.items():
                            if(k == 'list'):
                                todosEpisodios = v
                        
                        for EpPorEp, conteudo in todosEpisodios.items():
                            headers = {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'authority': 'embed.warezcdn.net'
                            }

                            data = {
                                'getAudios': conteudo['id']
                            }

                            page_video = requests.post('https://embed.warezcdn.net/serieAjax.php', data=data, headers=headers)
                            players = BeautifulSoup(page_video.content, 'html.parser')

                            for video in players:
                                valueVideo = json.loads(video)
                            
                                for m, n in valueVideo.items():
                                    if(m == 'list'):
                                        todosVideos = n
                                
                                for playerPorPlayer, conteudoVideo in todosVideos.items():
                                    if(len(todosVideos) == 2):
                                        if(conteudoVideo['audio'] == '2'):
                                            idPlayer = conteudoVideo['id']
                                    else:
                                        if(conteudoVideo['audio'] == '2'):
                                            idPlayer = conteudoVideo['id']
                                        else:
                                            idPlayer = conteudoVideo['id']

                            url_final = requests.get('https://embed.warezcdn.net/getPlay.php?id={}&sv=streamtape'.format(str(idPlayer)))
                            player_final = BeautifulSoup(url_final.content, 'html.parser')

                            data = player_final.find('script')

                            teste = data.text
                            teste = teste.replace('"', '').replace(';', '')
                            tamanho_link = len(teste)
                            posicao_link = teste.find('https')
                            legenda_link = teste.find('&c1_file=')

                            #link_final = teste[posicao_link:tamanho_link-2]

                            if(contadorEpisodios < 10):
                                nEpisodio = '0{}'.format(str(contadorEpisodios))
                            else :
                                nEpisodio = contadorEpisodios
                            
                            ## Verifica Legenda
                            if legenda_link == -1:
                                link_final = teste[posicao_link:tamanho_link-2]
                            else:
                                leg_eps['{}x{}'.format(str(arg_temporada), str(contadorEpisodios))] = teste[legenda_link+9:tamanho_link-21]
                                link_final = teste[posicao_link:]

                            nameArquivo = str(nome_serie) + str(arg_temporada) + 'x' + str(nEpisodio)
                            ## Aqui faz o envio do video para a pasta da série
                            url_pasta = 'https://api.streamtape.com/remotedl/add?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&url={}&folder={}&name={}'.format(str(link_final), str(ids_pasta_temporadas['T{}'.format(temporada+1)]), str(nameArquivo))
                            page_pasta = requests.get(url_pasta)
                            retorno_envio = BeautifulSoup(page_pasta.content, 'html.parser')

                            for retornoEnvio in retorno_envio:
                                vTemporario = json.loads(retornoEnvio)

                                for k, v in vTemporario.items():
                                    if(k == 'result'):
                                        link_episodio = str(v['link'].replace('/v/', '/e/'))

                                        encontrou_legenda = 0
                                        link_da_legenda = ''
                                        for pLeg in leg_eps:
                                            if pLeg == '{}x{}'.format(str(temporada+1), str(contadorEpisodios)):
                                                encontrou_legenda = 1

                                        if encontrou_legenda == 1:
                                            link_da_legenda = leg_eps['{}x{}'.format(str(temporada+1), str(contadorEpisodios))]

                            ## Aqui faz o envio das informações na nossa API
                            url_streamfilmes = 'https://streamfilmes.com/api/req_series.php?nome={}&imagen={}&titulo=DUBLADO&link={}&imdb={}&temporada={}&episodio={}&legenda={}'.format(str(nome_serie), str(url_banner), str(link_episodio), str(tmdb_serie), str(temporada+1), str(contadorEpisodios), str(link_da_legenda))
                            page_streamfilmes = requests.get(url_streamfilmes)

                            print("Episódio " + str(contadorEpisodios) + " - " + str(link_episodio))
                            contadorEpisodios = contadorEpisodios + 1
            client.messages.create(
                from_="+13155099696",
                body="Série: {} atualizada no Streamtape!".format(str(titulo)),
                to="+5548998062066"
            )
    else:
        print(termcolor.colored(color='green', text='[IGUAL]'))

        ## INICIA O PROCESSO DE BUSCA NOS EPISÓDIOS DA ÚLTIMA TEMPORADA PARA A COMPARAÇÃO
        # INICIA STREAMTAPE
        for temporada in todasPastas:
            if(temporada['name'] == 'T{}'.format(str(len(v['folders'])))):
                idTemporada = temporada['id']

                url_temporada = 'https://api.streamtape.com/file/listfolder?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&folder={}'.format(str(idTemporada))
                page_temporada = requests.get(url_temporada)
                retorno_temporada = BeautifulSoup(page_temporada.content, 'html.parser')

                for epTemporadas in retorno_temporada:
                    vEpTemp = json.loads(epTemporadas)

                    for k, v in vEpTemp.items():
                        if(k == 'result'):
                            totalEpisodios = len(v['files'])
                            todosEpisodios = v['files']

        # INICIA WAREZ
        for temporada in range(len(ids_temps)):
            if(temporada+1 == len(ids_temps)):
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'authority': 'embed.warezcdn.net'
                }

                data = {
                    'getEpisodes': ids_temps['{}'.format(temporada+1)]
                }

                page_episodios = requests.post('https://embed.warezcdn.net/serieAjax.php', data=data, headers=headers)
                episodios = BeautifulSoup(page_episodios.content, 'html.parser')
                
                for totalEpisodiosWarez in episodios:
                    tEpi = json.loads(totalEpisodiosWarez)
                
                for k, v in tEpi.items():
                    if(k == 'count'):
                        totalizadoEpisodios = v
        
        # COMPARA A QUANTIDADE DE EPISÓDIOS DA TEMPORADA
        print('Comparação de episódios: ', end='\r\t\t\t\t\t')
        if(totalEpisodios != len(v)):
            print(termcolor.colored(color='yellow', text='[DIFERENTE]'))
            if(totalEpisodios > len(v)):
                print(termcolor.colored(color='red', text='Streamtape tem mais episódios que o warez!'))
                continue
            else:
                diferencaEpisodios = (len(v) - totalEpisodios)
                print('Diferença: ', end='\r\t\t\t\t\t')
                print(termcolor.colored(color='yellow', text='{}'.format(str(diferencaEpisodios))))
                print('\n')
                print(termcolor.colored(color='blue', text='--> Iniciando o processo de correção dos episódios...'))
                print('--> Temporada: ' + str(temporada+1))
                print('\n')

                contadorEpisodios = totalEpisodios+1
                leg_eps = {}
                for percorre in episodios:
                    value = json.loads(percorre)

                    for k, v in value.items():
                        if(k == 'list'):
                            todosEpisodios = v
                    
                    for EpPorEp, conteudo in todosEpisodios.items():
                        if int(conteudo['name']) > totalEpisodios:
                            headers = {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'authority': 'embed.warezcdn.net'
                            }

                            data = {
                                'getAudios': conteudo['id']
                            }

                            page_video = requests.post('https://embed.warezcdn.net/serieAjax.php', data=data, headers=headers)
                            players = BeautifulSoup(page_video.content, 'html.parser')

                            for video in players:
                                valueVideo = json.loads(video)
                            
                                for m, n in valueVideo.items():
                                    if(m == 'list'):
                                        todosVideos = n
                                
                                for playerPorPlayer, conteudoVideo in todosVideos.items():
                                    if(len(todosVideos) == 2):
                                        if(conteudoVideo['audio'] == '2'):
                                            idPlayer = conteudoVideo['id']
                                    else:
                                        if(conteudoVideo['audio'] == '2'):
                                            idPlayer = conteudoVideo['id']
                                        else:
                                            idPlayer = conteudoVideo['id']

                            url_final = requests.get('https://embed.warezcdn.net/getPlay.php?id={}&sv=streamtape'.format(str(idPlayer)))
                            player_final = BeautifulSoup(url_final.content, 'html.parser')

                            data = player_final.find('script')

                            teste = data.text
                            teste = teste.replace('"', '').replace(';', '')
                            tamanho_link = len(teste)
                            posicao_link = teste.find('https')
                            legenda_link = teste.find('&c1_file=')

                            #link_final = teste[posicao_link:tamanho_link-2]

                            if(contadorEpisodios < 10):
                                nEpisodio = '0{}'.format(str(contadorEpisodios))
                            else :
                                nEpisodio = contadorEpisodios

                            ## Verifica Legenda
                            if legenda_link == -1:
                                link_final = teste[posicao_link:tamanho_link-2]
                            else:
                                leg_eps['{}x{}'.format(str(temporada+1), str(contadorEpisodios))] = teste[legenda_link+9:tamanho_link-21]
                                link_final = teste[posicao_link:]

                            nameArquivo = str(nome_serie) + str(temporada+1) + 'x' + str(nEpisodio)
                            ## Aqui faz o envio do video para a pasta da série
                            url_pasta = 'https://api.streamtape.com/remotedl/add?login=359f28c4fd8c5fcbe804&key=wadmxrpwmMSJvpe&url={}&folder={}&name={}'.format(str(link_final), str(idTemporada), str(nameArquivo))
                            page_pasta = requests.get(url_pasta)
                            retorno_envio = BeautifulSoup(page_pasta.content, 'html.parser')

                            for retornoEnvio in retorno_envio:
                                vTemporario = json.loads(retornoEnvio)

                                for k, v in vTemporario.items():
                                    if(k == 'result'):
                                        link_episodio = str(v['link'].replace('/v/', '/e/'))

                                        encontrou_legenda = 0
                                        link_da_legenda = ''
                                        for pLeg in leg_eps:
                                            if pLeg == '{}x{}'.format(str(temporada+1), str(contadorEpisodios)):
                                                encontrou_legenda = 1

                                        if encontrou_legenda == 1:
                                            link_da_legenda = leg_eps['{}x{}'.format(str(temporada+1), str(contadorEpisodios))]
                            
                            ## Aqui faz o envio das informações na nossa API
                            url_streamfilmes = 'https://streamfilmes.com/api/req_series.php?nome={}&imagen={}&titulo=DUBLADO&link={}&imdb={}&temporada={}&episodio={}&legenda={}'.format(str(nome_serie), str(url_banner), str(link_episodio), str(tmdb_serie), str(temporada+1), str(contadorEpisodios), str(link_da_legenda))
                            page_streamfilmes = requests.get(url_streamfilmes)

                            print("Episódio " + str(contadorEpisodios) + " - " + str(link_episodio))
                            contadorEpisodios = contadorEpisodios + 1
                
                print('\n')
                client.messages.create(
                    from_="+13155099696",
                    body="Série: {} atualizada no Streamtape!".format(str(titulo)),
                    to="+5548998062066"
                )
                            
        else:
            print(termcolor.colored(color='green', text='[IGUAL]'))

arquivoErros = open("seriesErros.txt", "w")
arquivoErros.writelines(seriesErros)

arquivoErros.close()
arquivo.close()