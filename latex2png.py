import xml.etree.ElementTree as ET
from requests import post, get
from pathlib import Path
from json import dumps
from time import sleep
from shutil import copyfileobj, copy


LATEX2PNG = 'http://latex2png.com'
LATEX2PNG_API = f"{LATEX2PNG}/api/convert"
base_path = Path('./parsed')
images_path = base_path.joinpath('images')
formulas_path = images_path.joinpath('formulas')

images_path.mkdir(exist_ok=True)
formulas_path.mkdir(exist_ok=True)

def get_urls():
  image_urls = {}
  for d in base_path.iterdir():
    if not d.is_dir() or not str(d).endswith('Engenharia de Computação 2019'):
      continue
    for f in d.iterdir():
      if not str(f).endswith('.xml'):
        continue
      root = ET.fromstring(f"<root>{f.read_text(encoding='utf8')}</root>")
      for child in root.iter():
        elements = child.findall('formula') or []
        for el in elements:
          data = {
            'auth': {
              'user': 'guest',
              'password': 'guest',
            },
            'latex': el.text,
            'resolution': 600,
            'color': '000000',
          }
          headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'Host': 'latex2png.com',
            'Origin': 'http://latex2png.com',
            'Referer': 'http://latex2png.com/',
          }
          r = post(LATEX2PNG_API, dumps(data), headers=headers)
          image_url = r.json().get('url')
          if not image_url:
            raise Exception(f"failed to generate image for '{el.text}'")
          image_urls[el.attrib.get('id')] = image_url[6:]
          print(el.attrib.get('id'), image_url)
          sleep(1)
  return image_urls


def download_urls(urls):
  downloaded = {}
  for id, url in urls.items():
    img_path = formulas_path.joinpath(f"{id}.png")
    if url in downloaded:
      copy(downloaded[url], img_path)
      continue

    r = get(f"{LATEX2PNG}/pngs/{url}", stream=True)
    with open(str(img_path), 'wb') as file:
      copyfileobj(r.raw, file)
    downloaded[url] = img_path
    sleep(0.1)

download_urls({"d4c86e30-c955-436b-8329-108d3c51a5cb": "704d427c0b28eccfb4b50a5ebf2fac0b.png", "c1c70b5f-751f-44cc-94ab-e43ed0d1c760": "962a9d6203f2c2d074f7de1caa45365b.png", "2da80b53-003c-42e5-93cc-c118c12551f5": "1c5322bbc3f376b1af30e641593e9f83.png", "1d3d1891-b8a0-413b-b28f-16c5fa646155": "d5b89c297bbfc4f3b7b824eb83764922.png", "29145124-d4e8-482c-84a0-c750c20e52f4": "735f8af029197c52c5e525e478b29e95.png", "391cee59-f1ee-4770-981e-42760b3f9c09": "d5b89c297bbfc4f3b7b824eb83764922.png", "b02a6b66-3766-4456-a4c5-d32436a8fa61": "735f8af029197c52c5e525e478b29e95.png", "e8091b1c-d91a-40b5-acf5-973bcfc0851c": "bcd2af90192cb19a599f6d349b37f73e.png", "5281c40f-a413-4f4e-b794-ba18b71e1c4b": "1b930f585e4335efa3dc9d8f2c62d5b5.png", "fad3e29d-4860-4cfc-a83f-15d9575885b1": "e3c5cc0bf65b23dfecd6bda8957a1523.png", "7196b117-a41c-4474-85b6-8efa5bd1d46d": "9137fac0125df890a70326ee7d009c1b.png", "d9f72931-e900-456b-87e3-3aa9eeefbf60": "dc3d783cc10b04ac3bb413928201a733.png", "3e774261-dc1f-41d8-b9a4-7dd8e4f9bd3e": "c08304a4a6a163ec23845c40e1ef17a0.png", "079229ea-6bd7-4398-9b5b-4c0841669971": "99dcefbd1cda3fd725f3c01051cd53b9.png", "cd0dc2ec-bd47-47b4-8d33-74f3a913f2b5": "54ea77052de8a774949c5ecc97ffad2e.png", "919ac0ac-6dfc-4981-ba2c-56f593c29b0e": "b2bceba2c191fba4ea62b719c4361280.png", "23d7746e-e576-476d-9d61-438d928602b8": "25b6b7b4b8a48d9383a472e084e9a34d.png", "f7b7c57b-b5ac-4a97-b2b5-5ffeff632e84": "9db772ed71302a0d4e46851101079390.png", "562ec016-7440-4ca1-9de2-4af2c28ce27f": "13b1121ce2850a5fe8d4961c241843c9.png", "143671be-a8e4-4390-9d89-be420854a653": "1a2b83f65b5b37e3161ae45a759645d1.png", "1e075706-dd43-4fe1-8eb8-86e4c85aaa9e": "31feed9c3300359de850f6422191aa90.png", "550eae1f-58d6-4b1c-ad00-40e42eccdef4": "a7bc6b6a6c3737c4542a9bb84b76e636.png", "82e3509c-9763-4836-9f3d-738ac4be8729": "1be358bcbacddb5189913c1eb2cb3cc0.png", "b8e0518c-21fc-4ef0-a96b-394512d2a124": "ffb3085017458a64544c55e92b0108fc.png", "913488fd-6e28-4f53-acd6-4ee32c028322": "9393889c79d8075aacb027370727727a.png", "66499b10-d4cc-4c0a-b87e-840068354afc": "cb5cd0181f7d88551ab87d03f38acc1d.png", "8fffd18e-b286-4741-8c32-3c26b2f27124": "5bfed37b7d0ea6e6ce4d54edb5900fc6.png", "e3ff3307-351a-4e7f-9be9-1109b74e44f8": "f5546d1409fad95a028f3e05976d47ff.png", "b5ab1616-8e66-4b8a-a79e-eb4d99f9d575": "ffb3085017458a64544c55e92b0108fc.png", "9a99772b-7c63-48e5-bb70-6d3b623ed928": "984d2d55d91d3bd7ee6aa9344bce30b2.png", "9da5bad7-e2fc-4900-860e-3d8d4b4d9b1a": "a45cb79b0faf3503eb5f3277b5429bc3.png", "f3d6a999-1d0d-40df-97ec-2282c7877ce5": "57b1a4d8d869a11f4fa4e95e4b03fc74.png", "23427ece-1175-4b26-a65f-674b2f50a4b7": "67710868c3d76a31f30a139b7a86b432.png", "3137d64d-230d-4bd3-9ced-36c9ae4eb6ee": "bbfd9c98c59197ecdf5c00ef2e23e931.png", "af27bc29-fe53-457b-8c97-c745f7bea3c3": "ab97f8a8ed5bb43d157c45d49c005cf1.png", "b5272396-bec8-423d-906c-3eb2dd50a815": "58f15279b9b6b7192b3650549dffd6a1.png", "8da5d8b1-ede2-40f8-add2-d93d290053c1": "1371c2d5257a3d69ed0ca68329bb5ca5.png", "f636ebf1-2870-4b30-99ab-ed1628f1add0": "5e0180acbbb245421bc4a8f993868d71.png", "db6ecd9a-b65b-4760-826e-35850c2f9174": "1693986ff1c63d399cc235333d47ec74.png", "5259035c-6bbf-4155-8986-17dc8811cfe8": "92a17e294619028009500a9fdcce8eb8.png", "8ce69025-af81-46da-9bfd-2453da4c4354": "da07c2b0788cdb3f5dc23b026d2232cc.png", "12bd7c7e-1937-40f8-a730-337301cc8466": "b5ae948abc2aaf6f585027bd26a4501c.png", "d390b535-b96f-4ffa-8de2-f91a89166a5b": "d5b89c297bbfc4f3b7b824eb83764922.png", "02d2168c-6251-49ee-8734-8190cbf17776": "4b68340e93b8829896423c39322c07b0.png", "6075761d-365f-40e8-9a44-2775561e6b8e": "6f06bf943c63fbf1c8ff2070c34bcd26.png", "f7d4f487-6af9-48be-a7af-04657091774d": "1d8919f761cd9c2a396da729d1533214.png", "0f07fbda-fcdd-4f74-aed3-370e7df777b0": "4b68340e93b8829896423c39322c07b0.png", "62f51547-612e-4fa7-b031-0836200649a2": "7227fa2e822abb6e0909ad753eaec558.png", "d683376f-3aff-4c05-9306-13946bcd8b3b": "c58a3cd2cab0ef5e47f26717f6b09786.png", "36a813a5-4ce9-436a-bc0c-45e0e9c25df5": "1693986ff1c63d399cc235333d47ec74.png", "6eeb30e5-2912-4b56-bb0b-20a267ad7b66": "57558557d72a829c8f9ab7f73f60c87a.png", "3fed6fde-ec26-44bf-809e-e2505c27c884": "c58a3cd2cab0ef5e47f26717f6b09786.png", "8c2e6b17-d7a1-4502-95ce-350eb7cad475": "1693986ff1c63d399cc235333d47ec74.png", "47f71bd8-3996-4e48-abec-1918024e91fb": "57558557d72a829c8f9ab7f73f60c87a.png", "63490170-9225-4eef-86fd-4510ef6dd287": "cd2d577b21edb8f1f1e6e837ac2ffcd4.png", "9051fc1d-428d-44b3-9e12-f154c3d0daf2": "1693986ff1c63d399cc235333d47ec74.png", "3cda0824-3ee0-40c1-91e4-c215b1d5f36f": "7227fa2e822abb6e0909ad753eaec558.png", "7156f9aa-f836-4587-8706-56ea25ef3d86": "cd2d577b21edb8f1f1e6e837ac2ffcd4.png", "c92eb71c-3136-4818-b974-db6f320ecb36": "1693986ff1c63d399cc235333d47ec74.png", "afae264a-861b-455d-ae80-5cfbcbf57d20": "5b787d8fc15d5e095e1a53d1a031d333.png", "35b9348c-71e3-4d5c-b683-fc00e6c18d1c": "cd2d577b21edb8f1f1e6e837ac2ffcd4.png", "8df35912-8b92-40cf-b859-acc1af961a1f": "1693986ff1c63d399cc235333d47ec74.png", "da001b4f-d351-42d3-955b-823e83c6afff": "5fcac5b12fcd88722cf9c543f4a05818.png", "1091a8e7-eeed-467c-b838-c1e85eef3487": "5fcac5b12fcd88722cf9c543f4a05818.png", "b9bb2953-322d-462a-ae78-92e9113cf54f": "5fcac5b12fcd88722cf9c543f4a05818.png", "587814d6-826f-48d5-af49-57700e089a89": "5fcac5b12fcd88722cf9c543f4a05818.png", "32850b13-1aa0-4842-a6d7-253accfc098f": "5fcac5b12fcd88722cf9c543f4a05818.png", "2f2612b2-ac4b-4285-9cf1-55702bd715d1": "bbd4950647444dcd17d6f8703d80e0ab.png", "e9a79ef4-3e3c-45bb-be7f-e302f77a4ffd": "cc87ed6c3c0d7972ccc3a2af6ca0ecb2.png", "015183c9-328e-4db7-8634-792d570e1681": "6f942aa863de84e2cb33661035166de9.png", "1522a1b9-17aa-4dd7-89b0-b4339a66a101": "f4fd63e7c1d5108c177ff32da316fce0.png", "97dcacf3-3371-4c5a-82d5-071e1bb4fe98": "b38b2c851cb14bf3208b5ea63a64ad34.png", "d2c42af6-af02-4738-a92d-78a3136b940f": "0229f9ad88d300b63347b1220f999158.png", "3531e6cd-83a6-4e55-a4aa-213feb664842": "b9aeafa2f6f7573b6ef5975dc1ed5898.png", "bbecf224-eb6e-4693-9302-37fade3d10fe": "b9aeafa2f6f7573b6ef5975dc1ed5898.png", "274e2b7a-ccbc-48fd-afe7-71ab586f4adf": "b9aeafa2f6f7573b6ef5975dc1ed5898.png", "95929e52-aec5-48cf-bd64-c0ce9cb059f4": "deaf0ad193142c9e637132fbd6c1e38c.png", "a0a7b1ef-438e-49ac-8d3b-3d38388ba49c": "e972d65952cecd404182e9e61598f03e.png", "498f773d-349e-41e8-9c0c-1883a82caef1": "b5e6eef5f1d7a60223959556308073aa.png", "a7a0e0f5-4ad1-4f20-8826-80132bf02c71": "f0d0153f1d44a9d385e7e44589b0feb9.png", "fe806b19-6f70-4b64-8e7c-06c3498e746d": "b9aeafa2f6f7573b6ef5975dc1ed5898.png", "766a4c0f-3038-4928-a608-256265f2f988": "d77e038c320e38d94d2f4b83d7587bde.png", "3d114356-fc7f-4123-8e37-121b39da9e31": "660e8494abb6e7dd42a8bd71879e1505.png", "84b7adea-72bb-4ad1-950c-c66736f99903": "765c4d86755c190d720688f957e9f411.png", "b770d5d9-d419-44d1-88ba-ba710b3ba9f4": "3b270b5105f8b4c47e8d7ffb9dfeaa95.png", "32fc911b-a24f-4210-a16f-0965e6f74ac5": "80fd032c410adf665305f87068170b79.png", "3355b79c-8fbd-4239-aa64-ed43a9bef860": "5e0180acbbb245421bc4a8f993868d71.png", "932331de-90d4-4984-954a-feb3dbf498a5": "3bdbf8c86bdb932e1bb85f603c892a50.png", "3b09d38f-54c9-4c64-8a4d-8a6a10f87a6a": "d66c158ef879ff875c75dc3817f5809c.png", "3cd987ca-0d5f-4735-9189-b0b83dcf7ff6": "e810b446e0b6d0a381bb1f24a6c5f72d.png", "5b904452-d3cf-43c3-8700-d3b3dc7cf85d": "339614ddee78df26486dd3303552dea0.png", "a2717367-dec5-427e-8285-5d88fdfbadc5": "b8293b266597d86b186a759419373c4d.png", "d12bdbcf-2be5-4258-b1d1-f1b36c99234f": "667c84fcf99fa883e21e413a6bde7847.png", "ef70d7fa-ab7c-49a1-8794-b942c24be1af": "47a3f1e3f652f5a7ed515f55420f0363.png", "6b07c55b-57ba-4c09-8db6-6398efcbde1b": "667c84fcf99fa883e21e413a6bde7847.png"})
