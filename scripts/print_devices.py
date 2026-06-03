import ctranslate2

cuda_devices = ctranslate2.get_cuda_device_count()

print("CUDA Available:", cuda_devices > 0)
if cuda_devices > 0:
    print("CUDA Device Count:", cuda_devices)
else:
    print("Using CPU fallback")
