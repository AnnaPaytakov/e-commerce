from django.contrib import messages
from django.shortcuts import render

class FormHandlerMixin:
    """Миксин для обработки форм и сообщений об ошибках"""
    
    form_class = None
    success_url = 'products-list'
    template_name = None

    def handle_form(self, request, form):
        """Обработка валидной формы, должен быть переопределен в классе"""
        raise NotImplementedError("Метод handle_form должен быть переопределен")

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.handle_form(request, form)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            return render(request, self.template_name, {'form': form})