; Определение шаблона для груза
(deftemplate cargo
  (slot weight (type NUMBER))
  (slot volume (type NUMBER))
  (slot fragile (type SYMBOL))
  (slot urgent (type SYMBOL))
  (slot route_risk (type SYMBOL)))

; Правила выбора транспорта
(defrule use_courier
  (cargo (weight ?w) (volume ?v) (urgent yes))
  (test (and (<= ?w 50) (<= ?v 0.5)))
  =>
  (assert (transport_type courier)))

(defrule use_truck_for_fragile
  (cargo (fragile yes))
  =>
  (assert (transport_type refrigerated_truck)))

(defrule use_air_for_urgent
  (cargo (weight ?w) (urgent yes))
  (test (> ?w 50))
  =>
  (assert (transport_type air)))

; Правило расчета рисков
(defrule high_risk_alert
  (cargo (route_risk high))
  =>
  (printout t "ВНИМАНИЕ! Выбран высокорисковый маршрут. Требуется дополнительная страховка." crlf))