import React, { useState, useEffect } from "react";
import axios from "axios";

const Lotes = () => {
  const [lotes, setLotes] = useState([]);  // Inicializar el estado como un arreglo vacío

  // Función para obtener los lotes de la API
  const fetchLotes = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/gestion_lotes/api/lotes/");
      console.log(response.data);  // Verifica qué contiene la respuesta
      setLotes(response.data);  // Establece los datos de la API en el estado 'lotes'
    } catch (error) {
      console.error("Error al obtener los lotes:", error);
    }
  };

  // Usamos useEffect para llamar a fetchLotes cuando el componente se monte
  useEffect(() => {
    fetchLotes();  // Llamamos a la función fetchLotes al cargar el componente
  }, []);  // El arreglo vacío asegura que solo se ejecute una vez cuando el componente se monta

  return (
    <div>
      <h1>Lotes</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre del Lote</th>
            <th>Fecha de Inicio</th>
          </tr>
        </thead>
        <tbody>
          {lotes.length > 0 ? (
            lotes.map((lote) => (
              <tr key={lote.id}>
                <td>{lote.id}</td>
                <td>{lote.nombre_lote}</td>
                <td>{lote.fecha_inicio}</td>
              </tr>
            ))
          ) : (
            <tr><td colSpan="3">No hay lotes disponibles</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Lotes;
