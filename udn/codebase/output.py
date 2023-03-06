# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo import errors
import csv
import os
import pymysql

# 新聞分類對應資料庫類別
category_list = {
    "要聞": 'important',
    "運動": 'sport',
    "全球": 'global',
    "社會": 'social',
    "產經": 'produce',
    "股市": 'stock',
    "生活": 'life',
    "文教": 'education',
    "評論": 'comment',
    "地方": 'local',
    "兩岸": 'cntw',
    "數位": 'digit',
    "閱讀": 'read',
    "Can't find it.": 'other'
}


def output_mysql(list_results):
    # 連線資料庫之資訊
    host = "140.117.69.136"
    user = "crawler"
    password = "lab_30241#"
    all_count = 0
    print("存入MySQL...")

    categoryResult = {'important': [], 'sport': [], 'global': [], 'social': [], 'produce': [], 'stock': [], 'life': [],
                      'education': [], 'comment': [], 'local': [], 'cntw': [], 'digit': [], 'read': [], 'other': []}

    table_list = []
    # 檢查年份
    connection = pymysql.connect(host, user, password, charset='utf8mb4')
    with connection.cursor() as cursor:
        for db_name in categoryResult.keys():
            cursor.execute("use crawler_udn_" + db_name)
            cursor.execute("SHOW TABLES")
            fet = cursor.fetchall()
            for k in fet:
                table_list.append(k[0])

    for dictResult in list_results:
        year = dictResult['artDate'][0:4]
        placeholders = '", "'.join(dictResult.values())
        columns = ', '.join(dictResult.keys())
        try:
            category = category_list[dictResult["artCatagory"]]
        # 沒出現在分類中則歸為 other 類
        except KeyError:
            category = 'other'
        # 檢查是否有該年份資料表
        table_name = category + "_" + year
        if table_name not in table_list:
            mysql_create_table(connection, category, table_name)

        categoryResult[category].append("REPLACE INTO %s ( %s ) VALUES ( %s )" % (table_name, columns, '"' + placeholders + '"'))

    # Connect to the database
    connection = pymysql.connect(host, user, password)
    for categoryName in categoryResult:
        if len(categoryResult[categoryName]) > 0:
            count = 0
            try:
                with connection.cursor() as cursor:
                    cursor.execute("use crawler_udn_" + categoryName)
                    for dictResult in categoryResult[categoryName]:
                        cursor.execute(dictResult)
                        count += 1
                        all_count += 1
                connection.commit()
            except Exception as e:
                # 方便找出錯誤
                print(e)
            finally:
                print("存入'crawler_udn_" + categoryName + "'資料庫，筆數:", count)
    connection.close()
    print('總存入筆數:', all_count)
    print('------------------------------------')
    return all_count


def mysql_create_table(connection, category, table_name):
    with connection.cursor() as cursor:
        cursor.execute("use crawler_udn_" + category)
        cursor.execute("CREATE TABLE  %s "
                       "(artTitle			VARCHAR(255)	NOT NULL,"
                       "artDate				datetime		NOT NULL,"
                       "artCatagory	VARCHAR(255)	NOT NULL,"
                       "artSecondCategory	VARCHAR(255)	NOT NULL,"
                       "artUrl				VARCHAR(160)	NOT NULL,"
                       "artContent			mediumtext		NOT NULL,"
                       "PRIMARY KEY (artUrl))" % table_name)


def output_mongo(mongouri, mongodb, mongocol, list_results):
    # 連上MongoDB
    try:
        client = MongoClient(mongouri)
        db = client[mongodb]
    except errors.ConnectionFailure as err:
        print(err)

    results = db[mongocol].insert_many(list_results)
    print(results.inserted_ids)


def output_csv(results, start_time, end_time, path):

    file_path = path + "UDN_" + start_time[0:10] + "_" + end_time[0:10] + '.csv'
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(file_path, 'w', newline='') as csv_file:
        # 定義欄位
        fieldnames = ['artTitle', 'artDate', 'artCatagory', 'artSecondCategory', 'artUrl', 'artContent']

        # 將 dictionary 寫入 CSV 檔
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # 寫入第一列的欄位名稱
        writer.writeheader()

        # 寫入資料
        for r in results:
            writer.writerow(r)

        print('儲存位置: ' + os.path.dirname(file_path))
        print('檔名: ' + os.path.basename(file_path) + ' 匯出完成')
        print('總筆數:', len(results))


if __name__ == "__main__":
    results = [
        {
            'artTitle': '如何避免孩子誤食危機？預防孩子誤食8方法',
            'artDate': '2019-06-04 12:54:00',
            'artCatagory': '生活',
            'artSecondCategory': '家庭兩性',
            'artUrl': 'https://udn.com/news/story/7272/3843574',
            'artContent': '【作者：巫漢盟（阿包醫生）】之前跟大家分享「孩子不吃飯，請先別急著給營養補充品！」，有不少粉絲留言想聽可怕的故事，所以這次阿包醫生就來分享啦！ 維他命當糖果吞？一次吞了150顆故事是這樣的……有一天，以前大學學妹問我：「包子學長，想請問我同學小孩3歲半，剛剛吃了150顆維他命D，有送去急診，但醫師說他沒碰過，應該沒關係，就回去了，想確認一下有需要觀察什麼嗎，感覺毛毛的～」嗯~我聽了也很毛！因為這位孩子竟然一次吞下150顆維他命，這實在不是一個小數目呀！而且，即使是好吃的糖果，也沒有人一次吞150顆啊！不得不佩服這位小朋友，雖然聽媽媽說小孩看起來沒事，一切都正常...但我心裡整個緊繃起來，因為我已經想到後續會有的狀況，絕對不是家長能想像的....我馬上拿出計算機，計算他吃下去的維生素D劑量有無達到中毒濃度，因為過量攝取維生素D會造成高血鈣、高尿鈣，症狀會有異常口渴，眼睛發炎，皮膚搔癢，厭食、嗜睡、腹瀉、頻尿等，以及鈣在血管壁、肝臟、肺部、腎臟、胃中的異常沈澱，出現關節疼痛等...甚至造成心律不整，嚴重亦會致命！好的，現在就來跟大家說明3個重點：1. 藥品、營養品應放在孩子拿不到的地方，來避免孩子誤食或過量攝取。2. 孩子懂事後，適時教導孩子服用藥品和補充品的目的。3. 從小就要教導孩子吃東西要適量，不能因為好吃就一直吃，對於營養補充品更要注意用量。誤食中毒好發於6歲以下，誤吞常客有這些根據台灣兒科醫學會資料顯示，超過一半以上的誤食中毒事件發生在小於6歲的孩童，尤其以口腔期階段的小寶寶最常見，他們會藉由刺激嘴巴、口腔和舌頭來得到本能滿足，另外，統計也發現，最常發生意外中毒的地方不是在外面，而是在家中。而不管誤食地點在哪，任何物品都可能造成兒童誤食，包括以下3類：1. 藥物：降血壓藥物、降血糖藥物、維他命藥片、兒童藥水等。2. 細小物品：玩具零件、鈕扣、電池、紅豆、綠豆、花生、迴紋針、硬幣等。3. 洗劑、化學藥劑：清潔劑、殺蟲劑、包粽強鹼水等。其中，電池、玩具零件更是寶包誤食的常客，曾有孩童因為誤吞電池，最後只能透過內視鏡取出，若是太晚發現，後果實在不堪設想。而誤食殺蟲劑或鹼水的孩子，阿包醫生之前在醫院的加護病房不時會遇到，這些孩子即使渡過危險期，後面還有許多後遺症將會陪伴他們一輩子。預防孩子誤食8方法由於寶包好奇心旺盛，加上有的小零件或電池遠看真的很像小餅乾，孩子不易分辨，往往隨手一抓就往肚裡吞，最後只得就醫取出，這邊也提供以下8種方法，提供給爸媽參考。1. 確認環境安全爸媽應確保任何孩童可伸手觸碰的地方都是安全的，像是櫃子、電視、兒童床等。2. 存放好藥物所有藥物或保健食品應放在高櫃或不易開啟的安全瓶中。另外，兒童用藥由因為氣味芳香，因此也應放在孩子拿不到的地方，每次用完也應立即放回原處。3. 避免在兒童面前服藥避免在年紀較小的孩子面前吃藥，以免引起模仿。4. 確認藥物數量大人服藥時應默數數量，若有掉落要確實找出並丟棄。5. 謹慎處理過期藥物過期或未用完的藥物應確實回收。6. 確實收好危險物品清潔用品、殺蟲劑等化學藥劑應存放在鎖櫃。另外，若突然有事應暫緩手邊工作，並先將正在服用的藥物或整理家務的清潔劑收好再去，許多誤食事件都是在此時發生。7. 勿用食品容器分裝有毒物切勿用食品容器分裝有毒的液體或粉末，例如：鹼粽水、農藥，曾有孩童誤食導致食道灼傷，甚至死亡。8. 確實收好零碎物品所有可能誤食的物品應放在兒童無法開啟的鎖櫃中，例如：迴紋針、圖釘、磁鐵、硬幣、瓜子、綠豆、花生。當孩子誤食，第一時間這樣做若是孩子不慎誤食或疑似中毒，請爸媽依照誤食狀況遵照以下方法，但若是無法確定自己能否處理，應直接撥打119送醫。狀況1：吞入異物→移除、避免催吐若是孩子不慎吞入異物，首先要先確認該物品為何，若是用肉眼就可看見位於口腔的物品，那麼可立即移除；但如果看不到，則不管是哪一種物品都不建議催吐，並且應盡快送醫，因為若孩子吞下的是有機溶劑，在催吐過程中可能會造成吸入性肺炎，若是強鹼水則可能造成二度灼傷。狀況2：確認噎到→拍背壓胸或哈姆立克法噎到狀況有兩種，第一種是若吞入的異物卡在上呼吸，造成阻塞或窒息，而且也無法發出聲音，那麼可以利用拍背壓胸或哈姆立克法，將異物藉由肺部氣流或腹壓噴出。第二種是可以發出聲音，但呼吸有咻咻聲，那麼異物應該未完全阻塞，或卡在下呼吸道，應儘速就醫取出。狀況3：不確認物品→盡速就醫第三種則是不確認孩子吞入的物品有無危險性，建議先詢問孩子吃進了什麼，同時將殘餘部分或可疑藥物和藥物包裝包好，並且盡速送醫，到醫院後應提供給醫護人員參考。也可撥打台北榮總臨床毒物與職業醫學科電話諮詢，(02)2871-7121。若是玩具的殘餘零件，可幫助醫師判斷能否在X光片中看到；若是藥物包裝或說明書則可以提供醫師正確藥名，甚至是中毒處理方法。最後也提醒爸媽，除了將預防方法學起來外，平時也該注意孩子的狀況！當孩子有異狀，像是呼吸困難、手緊抓著脖子、說不出話、臉部脹紅、嘴唇發紫、劇烈咳嗽等，都是誤食或中毒的徵兆，應該立即停下手邊工作查看，才能確保寶包安全無虞喔！對了，故事的最後，好在那位孩子服用的維生素D劑量尚未達到中毒濃度，並且後續追蹤也無出現高血鈣及高尿鈣的症狀，讓我鬆了一口氣！但我永遠會記得他吃了150顆的這件事，並引以為鑑！【延伸閱讀】●小小孩老是說「不要」？試試這5種方法，從「不要」改成「好啊！」●「毛巾綁腿退燒法」行不行？四位醫師這樣解答'
        }, {
            'artTitle': '中獎5千萬卻揮霍無度 39歲男子因竊盜被捕',
            'artDate': '2019-06-18 14:29:00',
            'artCatagory': '全球',
            'artSecondCategory': '世界萬象',
            'artUrl': 'https://udn.com/news/story/6812/3878561',
            'artContent': ' 南韓釜山蓮堤區刑警日前破獲一起連續竊盜案，這名歹徒潛入當地與大邱的16家餐廳，最終在搭乘計程車時露出形蹤。而後發現該名歹徒竟是13年前的彩券頭獎得主，不只19億韓元(約5048萬台幣)獎金全花光，還因竊盜多次進出警局。據韓媒《SBS》報導，該名男子今年39歲，在2006年時曾獨得19億韓元(約5048萬台幣)的彩券獎金，就算扣除稅收也還有將近3723萬台幣。男子最初經常往家裡送錢、貼補家用，但卻也開始賭博、進入聲色場所，最終在8個月內光積蓄。警方透露，男子在獎金花光後經濟陷入困境，當時男子早有竊盜前科，因此重操舊業，在某次行竊珠寶店被捕，入獄服刑1年，沒想到出獄後繼續轉往釜山與大邱的16家餐廳和服飾店偷錢，共得手3600萬韓元(約96萬台幣)。在警方追查歹徒線索時發現，歹徒曾向計程車炫耀中獎事蹟，最後才順利鎖定嫌疑人、逮捕到案。一名刑警向媒體透露，「彩券頭獎本該成為該名男子的人生轉捩點，可惜他太過揮霍，又再度返回可悲的生活。我希望在這次服刑結束後，他能夠真正的改過，好好地重新開始。」'
        }, {
            'artTitle': '科學家發現腸道細菌製造的酶 能協助將A型血轉為O型血',
            'artDate': '2019-06-19 13:01:00',
            'artCatagory': '知識科技',
            'artSecondCategory': '科技新報',
            'artUrl': 'https://udn.com/news/story/6897/3880086',
            'artContent': '【文‧Emma stein】每個人自胚胎成形那天起就確定了血型，老死不會再改變，其中 O 型血是世上最普遍也最有價值的血型，所有血型都能接受 O 型血輸血，然而 O 型血只能接受 O 型血。不過現在，輸血規則可能要打破了，一群研究人員發現由人體腸道細菌產生的兩種酶，可以將 A 型血轉換為萬用 O 型血，或有助於解決血庫告急問題。人體最常見的 4 種血型為 A 型、B 型、O 型以及 AB 型，分類依據為紅血球表面的抗原不同，A 型血的紅血球表面有 A 型抗原（B 型血剛好跟 A 型血相反，B 型血的紅血球表面有 B 型抗原），因此若 A 型血的人接收 B 型血輸血，免疫系統就會注意到 B 型抗原的存在並攻擊紅血球，引發紅血球不正常分解而導致組織缺氧死亡的溶血反應。O 型血的紅血球表面則沒有 A 也沒有 B 型抗原，因此可以輸血給任何一種血型的人，當面臨緊急情況時，O 型血就是全能輸血者。然而這樣仍不夠。儘管 O 型血人口最多，有些國家偏偏以其他血型為主，比如日本人以 A 型血居多，因此科學家突發奇想，不如試試看將第二常見的 A 型血轉為通用血型？ 十多年前，科學家就已經開始尋求能將各種血型轉化\u200b\u200b為 O 型血的酶，雖然過去已找到一種酶能去除 B 型抗原有害醣分子（A 型和 B 型抗原由類似的碳水化合物分子組成），但是效率太低。由加拿大英屬哥倫比亞大學（UBC）化學生物學家 Stephen Withers 領導的團隊，決定改從腸道細菌尋找其他酶。科學家已經知道有些腸道細菌比如 Flavonifractor plautii，會「吃掉」一種稱為黏液素（Mucins）的蛋白，而這種蛋白的醣與 A 型血紅血球表面抗原的醣分子類似；換句話說，可以試試看利用腸道細菌的酶來吃掉 A 型血的紅血球表面抗原，使 A 型血轉變成萬用血型。於是研究人員從人體糞便樣本尋找 Flavonifractor plautii 腸道菌，並分離出特定 DNA 片段（編碼消化黏液素的基因），接著將這些 DNA 片段移植到大腸桿菌培養皿中製造酶，隨後測試它們消除 A 型血紅血球表面抗原的能力。剛開始時什麼事情都沒發生。然而當研究人員同時測試兩種酶，神奇的事發生了，這種腸道細菌酶真的可以消除掉有害抗原醣分子！這項發現對輸血來說具有極大應用前景，因為這說明可通用的輸血血液量將翻倍。目前研究還處於早期研究階段，研究人員必須繼續觀察酶是否能清乾淨 A 型血紅血球表面的所有抗原，也要確認酶是否會無意中改變紅血球其他功能。新論文發表在《自然-微生物學》（Nature Microbiology）期刊。   【本文章由科技新報授權提供，更多精彩內容請詳科技新報官網】 分享   facebook     '
        }]
    output_mysql(results)
