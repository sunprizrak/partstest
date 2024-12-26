# docker image
docker images                                   # посмотреть образы
docker build -t partstest .                     # собрать образ, если запускается не из папки проекта, указать полный путь к Dockerfile
docker image rm 'id_image'                      # удалить образ
# docker container
docker run -it --rm --name partstest partstest  # -it запуск контейнера в интерактивном режиме, --rm автоудаление после завершения, --name название контейнера, partstest назв. образа

# для запуска в фоновом режиме используйте tmux

# tmux
tmux new -s test_app     #создание новой сессии, test_app название сессии
ctr + b и после жмём d   # отсоединение от сессии
tmux attach -t test_app  # присоединение к сессии