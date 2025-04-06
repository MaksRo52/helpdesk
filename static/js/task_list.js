$(document).ready(function () {
    const audio = new Audio(notificationSoundPath); // Звук уведомления
    let originalTitle = document.title;
    let blinkInterval;
    let currentPageUrl = window.location.href; // Текущий URL страницы

    // Получение ID последней задачи из HTML
    function getFirstTaskId(taskListHtml) {
        const wrapper = $('<div>').html(taskListHtml);
        const firstTask = wrapper.find('.task').first();
        return firstTask.length ? parseInt(firstTask.data('id')) : 0;
    }

    // Мигание заголовка вкладки при новом уведомлении
    function startBlinking() {
        if (!blinkInterval) {
            blinkInterval = setInterval(() => {
                document.title = document.title === originalTitle ? "🔔 Новые задачи!" : originalTitle;
            }, 1000);
        }
    }

    // Остановка мигания заголовка
    function stopBlinking() {
        clearInterval(blinkInterval);
        blinkInterval = null;
        document.title = originalTitle;
    }

    // Обновление списка задач через AJAX
    function updateTaskList() {
        const data = $('#filters-form').serialize(); // Получаем данные фильтров

        $.ajax({
            url: currentPageUrl,
            data: data,
            type: 'GET',
            cache: false,  // Отключаем кэширование
            headers: { 'X-Requested-With': 'XMLHttpRequest' }, // Явно указываем, что это AJAX-запрос
            success: function (response) {
                const currentFirstTaskId = getFirstTaskId($('#task-list-container').html());
                const newLastTaskId = getFirstTaskId(response);

                // Если появилась новая задача
                if (newLastTaskId > currentFirstTaskId) {
                    $('#task-list-container').html(response); // Обновляем список задач
                    audio.play(); // Звук уведомления
                    startBlinking(); // Запускаем мигание заголовка

                    // Обновляем URL с фильтрами в истории
                    history.pushState(null, '', currentPageUrl + '?' + data);
                }
            },
            error: function (xhr) {
                console.error('Ошибка при обновлении задач:', xhr);
            },
        });
    }

    // Периодическое обновление каждые 10 секунд
    setInterval(updateTaskList, 10000);

    // Останавливаем мигание, когда пользователь возвращается к вкладке
    $(window).focus(function () {
        stopBlinking();
    });

    // Сброс фильтров
    $('#reset-filters').on('click', function () {
        window.location.href = window.location.pathname; // Перезагрузка страницы без фильтров
    });

    // Обновляем URL при навигации по истории (кнопки "Назад" / "Вперёд")
    $(window).on('popstate', function () {
        currentPageUrl = window.location.href;
        updateTaskList();
    });
});