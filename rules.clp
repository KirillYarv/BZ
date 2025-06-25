
;ШАБЛОНЫ 

(deftemplate warehouse
  (slot id)
  (slot location)
  (multislot products))

(deftemplate product
  (slot name)
  (slot shelf_life (type NUMBER))
  (slot storage_conditions))

(deftemplate request
  (slot id)
  (slot product)
  (slot quantity (type NUMBER))
  (slot destination)
  (slot priority))  ;; low, medium, high

(deftemplate shipment
  (slot product)
  (slot from)
  (slot to)
  (slot status))

(deftemplate candidate_warehouse
  (slot product)
  (slot warehouse_id))

(deftemplate alert
  (slot type)
  (slot product))

;ФАКТЫ

(deffacts initial_data
  (warehouse (id W1) (location "Москва") (products "товар_А" "товар_B"))
  (warehouse (id W2) (location "Казань") (products "товар_C" "товар_A"))

  (product (name "товар_А") (shelf_life 2) (storage_conditions "сухое, +5°C"))
  (product (name "товар_B") (shelf_life 10) (storage_conditions "прохладное, +10°C"))
  (product (name "товар_C") (shelf_life 5) (storage_conditions "влажное, +4°C"))
  (product (name "товар_D") (shelf_life 5) (storage_conditions "влажное, +4°C"))

  (request (id R12) (product "товар_А") (quantity 50) (destination "СПб") (priority high))
  (request (id R13) (product "товар_C") (quantity 20) (destination "Самара") (priority medium))
)

;ПРАВИЛА

(defrule select_warehouse
  (request (product ?p))
  (warehouse (id ?w) (products $?list&:(member$ ?p ?list)))
  =>
  (assert (candidate_warehouse (product ?p) (warehouse_id ?w)))
  (printout t "[INFO] Найден склад " ?w " для продукта " ?p crlf))

(defrule schedule_shipment
  (candidate_warehouse (product ?p) (warehouse_id ?w))
  (request (product ?p) (destination ?d))
  =>
  (assert (shipment (product ?p) (from ?w) (to ?d) (status scheduled)))
  (printout t "[OK] Отгрузка " ?p " из " ?w " в " ?d " запланирована." crlf))

(defrule check_expiration
  (product (name ?p) (shelf_life ?days&:(< ?days 3)))
  =>
  (assert (alert (type "expiration_risk") (product ?p)))
  (printout t "[ALERT] Товар " ?p " близок к окончанию срока годности!" crlf))

(defrule high_priority_notice
  (request (id ?id) (priority high))
  =>
  (printout t "[NOTICE] Обнаружена заявка высокого приоритета: " ?id crlf))
