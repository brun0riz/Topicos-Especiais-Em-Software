from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter
from bs4 import BeautifulSoup


def encontrar_produtos(driver):
    lista = []
    for prod in range(1, 4):
        produtos_lista = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'Hits_ProductCard__Bonl_'))
        )

        for produto in produtos_lista:
            link_produto = produto.find_element(By.TAG_NAME, 'a').get_attribute('href')
            nome_produto = produto.find_element(By.CLASS_NAME, 'ProductCard_ProductCard_Name__U_mUQ').text
            preco_produto = produto.find_element(By.CLASS_NAME, 'Text_MobileHeadingS__HEz7L').text

            lista.append([nome_produto, preco_produto, link_produto])
        if prod < 3:
            try:
                nb = driver.find_element(By.CSS_SELECTOR, '[data-testid="page-next"]')
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", nb)
                sleep(1)
                nb.click()
                sleep(5)
            except Exception as e:
                print(f"Erro ao mudar de página: {e}")
    return lista


def contar_aparicoes(lista1, lista2, lista3):
    todas_listas = lista1 + lista2 + lista3
    nomes_produtos = [produto[0] for produto in todas_listas]
    contagem = Counter(nomes_produtos)
    return contagem


def pegar_top_produtos(contagem, todas_listas, n=5):
    top_produtos = contagem.most_common(n)
    produtos_final = []
    for nome_produto, _ in top_produtos:
        for produto in todas_listas:
            if produto[0] == nome_produto:
                produtos_final.append(produto)
                break
    return produtos_final


def coletar_caracteristicas(driver, link_produto):
    driver.get(link_produto)

    try:
        caracteristicas = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ProductSpecifications_classNameOuElemento'))
        )
        return caracteristicas.text
    except Exception as e:
        print(f"Erro ao coletar características: {e}")
        return "Características não encontradas."


def salvar_em_arquivo(dados):
    with open('produtos_configuracoes.txt', 'w') as arquivo:
        for produto in dados:
            arquivo.write(f"Nome: {produto[0]}\n")
            arquivo.write(f"Preço: {produto[1]}\n")
            arquivo.write(f"Link: {produto[2]}\n")
            arquivo.write(f"Configurações:\n{produto[3]}\n")
            arquivo.write("-" * 50 + "\n")


def descricao():
    


driver = webdriver.Chrome()

driver.get('https://www.zoom.com.br/')
sleep(3)

busca = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'SearchRegion_searchRegion__Z9Y6c'))
)

pesquisa = busca.find_element(By.TAG_NAME, 'div')
input1 = pesquisa.find_element(By.TAG_NAME, 'input')
input1.send_keys('Mouse Logitech')
input1.send_keys(Keys.ENTER)

lista_normal = encontrar_produtos(driver)

driver.get('https://www.zoom.com.br/search?q=Mouse%20Logitech')
sleep(3)

busca2 = driver.find_element(By.TAG_NAME, 'select')
sleep(1)
busca2.click()

filtro = busca2.find_element(By.XPATH, '//option[text()="Menor preço"]')
sleep(1)
filtro.click()
sleep(5)

lista_menor_preco = encontrar_produtos(driver)

driver.get('https://www.zoom.com.br/search?q=Mouse%20Logitech')
sleep(3)

busca3 = driver.find_element(By.TAG_NAME, 'select')
sleep(1)
busca3.click()

filtro2 = busca3.find_element(By.XPATH, '//option[text()="Melhor avaliado"]')
sleep(1)
filtro2.click()
sleep(5)

lista_melhor_avaliado = encontrar_produtos(driver)

contagem_produtos = contar_aparicoes(lista_normal, lista_menor_preco, lista_melhor_avaliado)

todas_listas = lista_normal + lista_menor_preco + lista_melhor_avaliado

top_produtos = pegar_top_produtos(contagem_produtos, todas_listas, n=5)

produtos_final = []

for produto in top_produtos:
    nome = produto[0]
    preco = produto[1]
    link = produto[2]

    configuracoes = coletar_caracteristicas(driver, link)

    produtos_final.append([nome, preco, link, configuracoes])

salvar_em_arquivo(produtos_final)

driver.quit()
