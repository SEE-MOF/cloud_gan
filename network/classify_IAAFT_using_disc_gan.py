import datetime

import h5py
import torch
import numpy as np
import matplotlib.pyplot as plt
from os import path
# from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create one file with all cloudsat_scenes
from GAN_discriminator import GAN_discriminator
from GAN_generator import GAN_generator

n_bins = 10
aspect=1/10
location = './'
file_string = location + 'IAAFT_generated_scenes_GAN_testset' + '.h5'
hf = h5py.File(file_string, 'r')
device = torch.device("cuda:0" if (torch.cuda.is_available()) else "cpu")
print(device)

iaaft_scenes = torch.tensor(hf.get('iaaft_scenes'))
iaaft_scenes_temp = torch.ones([len(iaaft_scenes),1,64,64])
print(iaaft_scenes_temp.shape)
iaaft_scenes_temp[:,0,:,:] = iaaft_scenes[:,:,:]
iaaft_scenes=iaaft_scenes_temp
#iaaft_scenes = torch.transpose(iaaft_scenes,2,3)
print(iaaft_scenes.shape)
print(iaaft_scenes[0:10])

H_disc=[5, 256, 128, 128, 5, 1, 64, 128, 256, 256, 4096, 1]
H_gen=[384,16384, 256, 128, 64, 1]
netG = GAN_generator(H_gen).float().to(device)
netD = GAN_discriminator(H_disc).float().to(device)
location_of_network_parameters = './gan_training_results_ver_4/'
checkpoint = torch.load(location_of_network_parameters + 'network_parameters_2400.pt', map_location=torch.device('cpu'))
netD.load_state_dict(checkpoint['model_state_dict_disc'])
location_of_network_parameters = './gan_training_results_ver_4/'
checkpoint = torch.load(location_of_network_parameters + 'network_parameters_2400.pt', map_location=torch.device('cpu'))
netG.load_state_dict(checkpoint['model_state_dict_gen'])
epoch = checkpoint['epoch']
output_folder = './early_epochs/gan/' + str(epoch) +'/'


b_size = (17444)//100
D_in_gen = [b_size, 64, 6]

f1, ax1 = plt.subplots(1, 1, figsize=(10.5,15))
f2, ax2 = plt.subplots(1, 1, figsize=(10.5,15))
f3, ax3 = plt.subplots(1, 1, figsize=(10.5,15))
f4, ax4 = plt.subplots(1, 1, figsize=(10.5,15))
f5, ax5 = plt.subplots(1, 1, figsize=(10.5,15))

print('starting cs training data')

location = './rr_data/'
file_string = location + 'cloudsat_training_data_conc' + '.h5'
hf = h5py.File(file_string, 'r')
cloudsat_scenes = torch.tensor(hf.get('cloudsat_scenes'))
#cloudsat_scenes = (cloudsat_scenes+1)*(55/2)-35
#cloudsat_scenes=torch.transpose(cloudsat_scenes,2,3)
print(cloudsat_scenes.shape)

for i in range(0,100):
    index1 = (i*len(cloudsat_scenes))//100
    index2 = index1 + len(cloudsat_scenes)//100
    output_cs_temp = netD(None,cloudsat_scenes[index1:index2].to(device)).cpu().detach().numpy()
    if i == 0:
        output_cs = output_cs_temp
    else:
        output_cs= np.append(output_cs,output_cs_temp,axis=0)
print(np.average(output_cs))
print(torch.max(cloudsat_scenes))
print(torch.min(cloudsat_scenes))


mean_disc = np.mean(output_cs)


ax3.text(0.5,0.91, 'Training set', transform = ax3.transAxes,fontsize = 26,color='black', horizontalalignment='center')
ax3.text(0.5,0.85,r'$\mu =$ ' +"%.4f" %(mean_disc), transform = ax3.transAxes,fontsize = 26,color='black', horizontalalignment='center')

ax3.hist(output_cs,bins = n_bins, range=(0,1), density=True)
#ax3.plot(output_cs,'.')
ax3.set_ylabel("Frequency", fontsize=28)
ax3.set_xlabel("Probability", fontsize=28)
ax3.tick_params(axis='both', which='major', labelsize=26)

ax3.set_ylim(0, 10)
ax3.set_aspect(aspect)
f3.savefig(output_folder + 'histogram_cs_training_classified_by_disc_gan_test_' + str(epoch))
print('Finished with cs plot_training')


print('starting cs test data')

location = './rr_data/'
file_string = location + 'cloudsat_test_data_conc' + '.h5'
hf = h5py.File(file_string, 'r')
cloudsat_scenes = torch.tensor(hf.get('cloudsat_scenes'))
#cloudsat_scenes = (cloudsat_scenes+1)*(55/2)-35
#cloudsat_scenes= torch.transpose(cloudsat_scenes,2,3)
output_cs = netD(None,cloudsat_scenes.to(device)).cpu().detach().numpy()
print(np.average(output_cs))
print(torch.max(cloudsat_scenes))
print(torch.min(cloudsat_scenes))

mean_disc = np.mean(output_cs)

ax4.text(0.5,0.91, 'Test set', transform = ax4.transAxes,fontsize = 26,color='black', horizontalalignment='center')
ax4.text(0.5,0.85,r'$\mu =$ ' +"%.4f" %(mean_disc), transform = ax4.transAxes,fontsize = 26,color='black', horizontalalignment='center')



ax4.hist(output_cs,bins = n_bins, range=(0,1), density=True)
#ax3.plot(output_cs,'.')
ax4.set_xlabel("Probability",fontsize = 28)
ax4.set_ylabel("Frequency", fontsize=28)
ax4.tick_params(axis='both', which='major', labelsize=26)



ax4.set_ylim(0, 10)
ax4.set_aspect(aspect)
f4.savefig(output_folder + 'histogram_cs_test_classified_by_disc_gan_test_' + str(epoch))

print('Finished with cs plot test')

print('starting generated gan')


for i in range(0,100):
    noise = (torch.randn(D_in_gen)).to(device)
    print(i)
    generated = netG(noise, None)
    generated = torch.transpose(generated,2,3)
    output_generated_part = netD(None,generated).cpu().detach().numpy()
    if i == 0:
        output_generated = output_generated_part
    else:
        output_generated = np.concatenate((output_generated,output_generated_part),axis=0)

#output_generated = output_generated.cpu().detach().numpy()
mean_disc = np.mean(output_generated)


ax1.text(0.5,0.91, 'GAN', transform = ax1.transAxes,fontsize = 26,color='black', horizontalalignment='center')
ax1.text(0.5,0.85,r'$\mu =$ ' +"%.4f" %(mean_disc), transform = ax1.transAxes,fontsize = 26,color='black', horizontalalignment='center')




ax1.hist(output_generated,bins = n_bins,range=(0,1),density=True)
#ax1.plot(output_generated,'.')
ax1.set_ylabel("Frequency", fontsize=28)
ax1.set_xlabel("Probability", fontsize=28)
#ax1.set_title('GAN', fontsize=32)
ax1.tick_params(axis='both', which='major', labelsize=26)
ax1.tick_params(labelbottom=True)
ax1.tick_params(labelleft=True)
ax1.set_aspect(aspect)
ax1.set_ylim(0, 10)
f1.savefig(output_folder + 'histogram_generated_gan_classified_by_disc_gan_test_' + str(epoch))


print('starting iaaft')
output_iaaft = netD(None,iaaft_scenes.to(device)).cpu().detach().numpy()

print(output_iaaft.shape)


print(np.average(output_iaaft))


mean_disc = np.mean(output_iaaft)


ax2.text(0.5,0.91, 'IAAFT', transform = ax2.transAxes,fontsize = 26,color='black', horizontalalignment='center')
ax2.text(0.5,0.85,r'$\mu =$ ' +"%.4f" %(mean_disc), transform = ax2.transAxes,fontsize = 26,color='black', horizontalalignment='center')

ax2.hist(output_iaaft,bins = n_bins,range=(0,1),density=True)
#ax2.plot(output_iaaft,'.')
#ax2.set_title('IAAFT', fontsize=32)
ax2.tick_params(axis='both', which='major', labelsize=26)
ax2.tick_params(labelleft=True)
ax2.tick_params(labelbottom=True)

ax2.set_xlabel("Probability", fontsize=28)
ax2.set_ylim(0, 10)
ax2.set_aspect(aspect)
f2.savefig(output_folder + 'histogram_iaaft_classified_by_disc_gan_test_' + str(epoch))


print('Starting to load generated scenes CGAN')
location = './'
file_string = location + 'CGAN_generated_scenes_for_histogram_test_temp_' + '.h5'
hf = h5py.File(file_string, 'r')

all_generated_CGAN = torch.tensor(hf.get('all_generated'))
all_generated_CGAN = all_generated_CGAN.reshape(-1,1,64,64)

all_generated_CGAN = (all_generated_CGAN +35)*2/55 - 1
#all_generated_CGAN = torch.transpose(all_generated_CGAN,2,3)

output_cgan = netD(None,all_generated_CGAN.to(device)).cpu().detach().numpy()

mean_disc = np.mean(output_cgan)


ax5.text(0.5,0.91, 'CGAN', transform = ax5.transAxes,fontsize = 26,color='black', horizontalalignment='center')
ax5.text(0.5,0.85,r'$\mu =$ ' +"%.4f" %(mean_disc), transform = ax5.transAxes,fontsize = 26,color='black', horizontalalignment='center')


ax5.hist(output_cgan,bins = n_bins, range=(0,1), density=True)
#ax3.plot(output_cs,'.')
#ax5.set_title('CGAN', fontsize=32)
ax5.tick_params(axis='both', which='major', labelsize=26)
ax5.tick_params(labelleft=True)
ax5.tick_params(labelbottom=True)

ax5.set_xlabel("Probability", fontsize=28)
ax5.set_ylim(0, 10)
ax5.set_aspect(aspect)
f5.savefig(output_folder + 'histogram_cgan_classified_by_disc_gan_test_' + str(epoch))
print('Finished with cs plot')
