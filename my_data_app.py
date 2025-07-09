import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import plotly.express as px

def crawl(selected_url, pages, driver):
    #essayer de récupérer les numérros de pages
    try:
        pages_numbers = pages.split(',')
    except Exception as e:
        # En cas d'exception
        try:
            pages_numbers = pages.split('-')
            start = int(pages_numbers[0])
            end = int(pages_numbers[1])
            pages_numbers = range(start, end)
        except Exception as e:
            st.header("Veuillez renseigner les pages convenablement")
            return
    
    # Nous avons les pages ainsi que l'url
    # Il est temps de scrapper
    DF = pd.DataFrame() # We will be using it later
    for p in pages_numbers:
        url = selected_url+'?page='+str(p) # max_page for this url is 119
        # Get url
        driver.get(url)
        # Get containers
        containers = driver.find_elements(By.CSS_SELECTOR, "[class = 'col s6 m4 l3']")
        # Check that we have something
        len(containers)
        # tile to really scrap the data
        data = []
        for container in containers:
            try:
                prix_main_container = container.find_element(By.CLASS_NAME, "ad__card-price")
                prix = prix_main_container.find_element(By.CSS_SELECTOR, "a").text
                prix = prix[:-3] #removing the last 3 charcters (CFA) from price
                prix = prix.replace(" ", "")
                type_main_container = container.find_element(By.CLASS_NAME, "ad__card-description")
                type = type_main_container.find_element(By.CSS_SELECTOR, "a").text
                adress_main_container = container.find_element(By.CLASS_NAME, "ad__card-location")
                adress = adress_main_container.find_element(By.CSS_SELECTOR, "span").text
                image_link = container.find_element(By.CLASS_NAME, "ad__card-img").get_attribute('src')
                # Putting everything inside a dictionary
                dic = {
                    'type ':type,
                    'prix':prix,
                    'adresse':adress,
                    'image_lien':image_link
                    }
                # print(dic)
                data.append(dic)
            except Exception as e:
                print(e)
        df = pd.DataFrame(data)
        DF = pd.concat([DF, df], axis=0).reset_index(drop=True) # adding the index from 0 until the last instead of restting the index each time a new df is concatenated
    return DF


def scraper_plusieurs_pages():

    st.markdown("<h2 style='text-align: center; color: black;'>SCRAPER LES DONNEES DE COIN-AFRIQUE</h1>", unsafe_allow_html=True)
    st.markdown("""
    Cette partie permet de télécharger les données des articles (vêtements et chaussures pour hommes et enfants) sur coin-afrique
    * **Libraries python:** base64, pandas, streamlit, selenium, plotly
    * **Sources:**
    """)
    st.markdown("""
        * **https://sn.coinafrique.com/categorie/vetements-homme**,
        * **https://sn.coinafrique.com/categorie/chaussures-homme**,
        * **https://sn.coinafrique.com/categorie/vetements-enfants**,
        * **https://sn.coinafrique.com/categorie/chaussures-enfants**,
    """)

    # instatntiate chrome options
    options = webdriver.ChromeOptions()
    # Allow chrome to be execute in headless mode
    options.add_argument('headless=new')
    # instantiate chrome with the defined options
    driver = webdriver.Chrome(options=options)
    # Définir les Urls
    url_1 = "https://sn.coinafrique.com/categorie/vetements-homme",
    url_2 =  "https://sn.coinafrique.com/categorie/chaussures-homme",
    url_3 = "https://sn.coinafrique.com/categorie/vetements-enfants",
    url_4 = "https://sn.coinafrique.com/categorie/chaussures-enfants",
        

    # afficher les urls à sélectionner
    selected = st.selectbox(
        "Veuillez choisir l'Url à scraper",
        [
            url_1, 
            url_2, 
            url_3, 
            url_4
        ]
    )
    pages = st.text_input(
        "Veuillez entrer les pages séparées par des virgules , ou une plage séparée par un tiret - : ",
        placeholder='1-6'
        )
    
    # il est temps de scraper
    if selected and pages :

        df = crawl(selected, pages, driver)
        st.dataframe(df)

def charger_donnees_deja_scrapees_avec_web_scraper():
    st.markdown("<h2 style='text-align: center; color: black;'>TELECHARGER LES DONNEES DE COIN-AFRIQUE</h1>", unsafe_allow_html=True)
    st.markdown("""
    Cette partie permet de télécharger les données des articles (vêtements et chaussures pour hommes et enfants) sur coin-afrique
    * **Libraries python:** base64, pandas, streamlit, selenium.
    * **Source:** [Coin-Afrique](https://sn.coinafrique.com/).
    """)
    # Charger les données 
    load_(pd.read_csv('data/coin_afrique_vetements_homme.csv'), 'Vêtements pour hommes', '1')
    load_(pd.read_csv('data/coin_afrique_chaussures_homme.csv'), 'Chaussures pour hommes', '2')
    load_(pd.read_csv('data/coin_afrique_vetements_enfants.csv'), 'Vêtements pour enfants', '3')
    load_(pd.read_csv('data/coin_afrique_chaussures_enfants.csv'), 'Chaussures pour enfants', '4')

def nettoyer_donnees_scrapees():
    dfs = []
    df1 = pd.read_csv('data/coin_afrique_vetements_homme.csv')
    df2 = pd.read_csv('data/coin_afrique_chaussures_homme.csv')    
    df3 = pd.read_csv('data/coin_afrique_vetements_enfants.csv')
    df4 = pd.read_csv('data/coin_afrique_chaussures_enfants.csv')  
    for df in [df1, df2, df3, df4]:
        # df = df[['articles_links-href', 'prix', 'type_', 'adresse']]
        df.rename(columns={'articles_links-href':'articles_links_2'}, inplace=True)
        # df.shape
        df.describe()
        df.duplicated().sum()
        df.drop_duplicates(inplace=True)
        df.isna().sum()
        df['prix'] = df['prix'].str[:-3] #removing the last 3 charcters (CFA) from price
        df['prix'] = df['prix'].str.replace(' ','')
        df['prix'] = df['prix'].replace({'Prixsurdema' : -1})
        df.prix = df.prix.astype('float')
        dfs.append(df)
    return dfs

def dashboard_donnees_nettoyees(dfs):
    # définir les filtres
    st.sidebar.title('Filtres')
    prix = st.sidebar.multiselect('Prix', [])
    type = st.sidebar.multiselect('Type d\'article', [])
    adresse = st.sidebar.multiselect('Adresse', [])
    titres = ['Vêtements hommes', 'Chaussures hommes', 'Vêtements enfants', 'Chaussures enfants']

    for i in range(0, 4):
        df = dfs[i]
        titre = titres[i]
        st.subheader('Données filtrées '+titre)
        prix = st.sidebar.multiselect('Prix', df['prix'].unique(), default=df['prix'].unique())
        type = st.sidebar.multiselect('Type d\'article', df['type_'].unique(), default=df['type_'].unique())
        adresse = st.sidebar.multiselect('Adresse', df['adresse'].unique(), default=df['adresse'].unique())
        # DF filtree
        filtered_df = df[(df['prix'].isin(prix)) & (df['type_'].isin(type) & df['adresse'].isin(adresse))]
        # Afficher les métrics
        col1, col2, col3 = st.columns(3)
        col1.metric('Prix total', f'{filtered_df['prix'].sum():,} FCFA')
        col2.metric('Moyenne prix', f'{filtered_df['prix'].mean():.0f} FCFA')
        col3.metric('Nombre d\'articles trouvés', len(filtered_df))
        # Charts
        col = st.columns(1)
        articles_par_adresse = filtered_df.groupby('adresse').size()
        fig_bar = px.bar(articles_par_adresse, title='Nb d\'articles par adresse')
        st.plotly_chart(fig_bar, use_container_width=True)
        col = st.columns(1)
        # with col:
        articles_par_type = filtered_df.groupby('type_').size()
        fig_bar = px.bar(articles_par_type, title='Nb d\'articles par type')
        st.plotly_chart(fig_bar, use_container_width=True)
        # affichage
        # st.dataframe(filtered_df)

# Fonction de loading des données
def load_(dataframe, title, key) :

    if st.button(title,key):
        st.subheader('Afficher les dimensions du tableau')
        st.write('Data dimension: ' + str(dataframe.shape[0]) + ' lignes et ' + str(dataframe.shape[1]) + ' colonnes.')
        st.dataframe(dataframe)



def main():
    # configurer la page
    st.set_page_config(page_title='Les Données de coin-afrique', layout='wide')
    st.markdown("""
    <style>
    div.stButton {text-align:center}
    </style>""", unsafe_allow_html=True)
    # définir quelques styles liés aux box
    st.markdown('''<style> .stButton>button {
    font-size: 12px;
    height: 3em;
    width: 25em;
    }</style>''', unsafe_allow_html=True)
    # Scraper plusieurs pages et afficher
    scraper_plusieurs_pages()
    # charger les données deja scrapéées avec web scraper
    charger_donnees_deja_scrapees_avec_web_scraper()
    # Nettoyer les données issues du Web scraper
    dfs = nettoyer_donnees_scrapees()
    # Faire un dashboard des données nettoyées
    dashboard_donnees_nettoyees(dfs)
    # Evaluer l'application
    st.markdown("""
                [Evaluer l'application](https://ee.kobotoolbox.org/x/JYaLnhyu)""")

if __name__ == "__main__":
    main()