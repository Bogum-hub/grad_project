import torch
import io
from PIL import Image
from torchvision import models,transforms

m = models.resnet18()
num_ftrs = m.fc.in_features
m.fc = torch.nn.Linear(num_ftrs, 1890)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
m.load_state_dict(torch.load('model_state_1210.pth', map_location=torch.device('cpu')))
m = m.to(device)
m.eval()

# image -> tensor
def transform_image(image_bytes):
    transform = transforms.Compose([
                                    transforms.Resize(224),
                                    transforms.ToTensor(),
                                    transforms.Normalize(
                                        mean = [0.485, 0.456, 0.406],
                                        std = [0.229, 0.224, 0.225]
                                    )])
    
    image = Image.open(io.BytesIO(image_bytes))
    return transform(image).unsqueeze(0)

# predict
def get_pred(image_tensor):

    f = open('drug_name_1207.txt',encoding='utf-8', errors='ignore')
    a = f.read()
    a_list = a.split(',')
    b = list(a_list)
    f.close()

    image_tensor = image_tensor.to(device)
    outputs = m(image_tensor)

    _, test_indices = torch.sort(outputs, descending = True)
    ls=[0,0,0,0,0]
    p=[0,0,0,0,0]
    a = 0
    for i in test_indices[0][:5]:
        ls[a] = outputs[0][i].item()
        a+=1

    k = 0
    for i in ls:
        p[k] = (i-min(ls)+1)/(max(ls)-min(ls)+2)
        k+=1
    p = torch.Tensor(p)
    
    i = 0
    c = {}
    for idx in test_indices[0][:5]:
        c[b[idx]] = round(p[i].item()*100,2)
        i += 1
    return list(c.keys()), list(c.values())

########## old one ##########
# def get_pred(image_tensor):

#     f = open('drug_name_1203.txt',encoding='utf-8', errors='ignore')
#     a = f.read()
#     a_list = a.split(',')
#     b = list(a_list)
#     f.close()

#     image_tensor = image_tensor.to(device)
#     outputs = m(image_tensor)
#     percentage = torch.nn.functional.softmax(outputs, dim = 1)[0] * 100

#     _, test_indices = torch.sort(outputs, descending = True)

#     c = {}
#     for idx in test_indices[0][:5]:
#         c[b[idx.item()]] = round(percentage[idx].item(),2)
        
#     return list(c.keys()), list(c.values())