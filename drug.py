import torch
import io
from PIL import Image
from torchvision import models,transforms

model = models.resnet18(weights='ResNet18_Weights.DEFAULT')

PATH = "model1011.pth"
torch.save(model.state_dict(), PATH)
model.eval()

# image -> tensor
def transform_image(image_bytes):
    transform = transforms.Compose([
                                    transforms.Resize(256),
                                    transforms.CenterCrop(224),
                                    transforms.ToTensor(),
                                    transforms.Normalize(
                                        mean = [0.485, 0.456, 0.406],
                                        std = [0.229, 0.224, 0.225]
                                    )])
    
    image = Image.open(io.BytesIO(image_bytes))
    return transform(image).unsqueeze(0)

# predict
def get_pred(image_tensor):

    #找出index
    # outputs = model(image_tensor)
    # _, preds = torch.max(outputs, 1)
    # idx = preds.item()
    #依照index從list找出藥品
    f = open('m1011.txt',encoding='utf-8', errors='ignore')
    a = f.read()
    a_list = a.split(',')
    b = list(a_list)
    f.close()
    
    # # 測試softmax：前5
    c = {}
    outputs = model(image_tensor)
    percentage = torch.nn.functional.softmax(outputs, dim = 1)[0] * 100
    _, test_indices = torch.sort(outputs, descending = True)

    for idx in test_indices[0][:5]:
        c[b[idx.item()]] = round(percentage[idx].item(),2)
        
    return list(c.keys()), list(c.values())