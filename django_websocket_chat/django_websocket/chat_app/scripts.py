ls = [1,1,1,2,3,3,3]
dup_list = []

def duplicate_removing(list_number):
    print(1)
    for i in ls:
        if i not in dup_list:
            dup_list.append(i)
    return dup_list

sam = duplicate_removing(ls)
print(sam)

def check_palindrom(text):
    return text == text[::-1]

sample_text = check_palindrom("mom")
print(sample_text)

def reverse_list(list_of_numbers):
    rev_list = list()
    for i in list_of_numbers[::-1]:
        rev_list.append(i)
    return rev_list
a = reverse_list([1,2,3,4,5,6])
print(a)

def reverse_string(text):
    return text[::-1]

a = reverse_string('naga')
print(a)

num = [1,3,5,3,3,8,7,6]
num.sort()
print(num)

c = sorted(num)
print(c)