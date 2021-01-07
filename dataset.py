import torch
from torch.utils.data import Dataset, DataLoader, random_split
from util import load_csv
from model.util import subsequent_mask
from transformers import BertTokenizer
from torch.autograd import Variable

class TranslationDataset(Dataset):
  def __init__(self, tokenizer:BertTokenizer, file_path:str, max_length:int):
    pad_token_idx = tokenizer.pad_token_id
    csv_datas = load_csv(file_path)
    self.docs = []
    for line in csv_datas: # line[0] 한글, line[1] 영어
      input = tokenizer.encode(line[0],max_length=max_length,truncation=True)
      rest = max_length - len(input)
      input = torch.tensor(input + [pad_token_idx]*rest)

      target = tokenizer.encode(line[1], max_length=max_length, truncation=True)
      rest = max_length - len(target)
      target = torch.tensor(target + [pad_token_idx] * rest)

      doc=[
        input,                                        # input
        (input != pad_token_idx).unsqueeze(-2),       # input_mask
        target,                                       # target,
        self.make_std_mask(target, pad_token_idx),    # target_mask
        (target[...,1:] != pad_token_idx).data.sum()  # token_num
      ]
      self.docs.append(doc)
  @staticmethod
  def make_std_mask(tgt, pad_token_idx):
    "Create a mask to hide padding and future words."
    target_mask = (tgt != pad_token_idx).unsqueeze(-2)
    target_mask = target_mask & Variable(subsequent_mask(tgt.size(-1)).type_as(target_mask.data))
    return target_mask

  def __len__(self):
    return len(self.docs)
  def __getitem__(self, idx):
    return self.docs[idx][0], self.docs[idx][1], self.docs[idx][2], self.docs[idx][3], self.docs[idx][4]
