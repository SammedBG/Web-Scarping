import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [keyword, setKeyword] = useState('');
  const [pincode, setPincode] = useState('');
  const [pages, setPages] = useState(1);
  const [data, setData] = useState([]);
  const [pagesScraped, setPagesScraped] = useState(0);
  const [totalProducts, setTotalProducts] = useState(0);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleScrape = async () => {
    setLoading(true);
    const res = await axios.post('http://localhost:5000/scrape', {
      search_keyword: keyword,
      pincode,
      pages
    });
    setData(res.data.data);
    setPagesScraped(res.data.pages_scraped);
    setTotalProducts(res.data.total_products);
    setFileName(res.data.file_name);
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>🛍️ Amazon Product Cards</h1>
      <div style={styles.form}>
        <input placeholder="🔍 Keyword" value={keyword}
               onChange={e => setKeyword(e.target.value)} style={styles.input}/>
        <input placeholder="📍 Pincode" value={pincode}
               onChange={e => setPincode(e.target.value)} style={styles.input}/>
        <input type="number" min="1" placeholder="📄 Pages"
               value={pages} onChange={e => setPages(e.target.value)} style={styles.input}/>
        <button onClick={handleScrape} style={styles.scrapeButton}>🚀 Scrape</button>
        {fileName && (
          <a href={`http://localhost:5000/download/${fileName}`}
             download style={styles.downloadButton}>
            ⬇️ Download Excel
          </a>
        )}
      </div>

      {loading && <p style={{color:'#ff832b'}}>⏳ Scraping in progress…</p>}

      {!loading && totalProducts > 0 && (
        <>
          <p>✅ Pages: {pagesScraped} | 🛒 Products: {totalProducts}</p>
          <div style={styles.cardGrid}>
            {data.map((item,i) => (
              <div key={i} style={styles.card}>
                <img src={item.Image} alt="" style={styles.image}/>
                <h3 style={styles.title}>{item.Title}</h3>
                <p>⭐ {item.Rating}</p>
                <p>💸 {item["Discount Price"]} <s>{item["Original Price"]}</s></p>
                <p>📦 {item.Availability}</p>
                <a href={item.ProductLink} target="_blank" rel="noreferrer">
                  <button style={styles.linkButton}>View on Amazon</button>
                </a>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: {padding:'2rem',fontFamily:'Arial'},
  header: {color:'#0f62fe'},
  form: {display:'flex',gap:'1rem',flexWrap:'wrap',marginBottom:'1rem'},
  input: {padding:'10px',borderRadius:'5px',border:'1px solid #ccc'},
  scrapeButton: {padding:'10px 20px',backgroundColor:'#0f62fe',color:'#fff',border:'none',borderRadius:'5px',cursor:'pointer'},
  downloadButton: {padding:'10px 20px',backgroundColor:'#24a148',color:'#fff',borderRadius:'5px',textDecoration:'none'},
  cardGrid: {display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(250px,1fr))',gap:'1rem'},
  card: {border:'1px solid #ddd',borderRadius:'8px',padding:'1rem',textAlign:'center',boxShadow:'0 2px 5px rgba(0,0,0,0.1)'},
  image: {width:'100%',height:'180px',objectFit:'contain'},
  title: {fontSize:'1rem',height:'3em',overflow:'hidden',margin:'0.5em 0'},
  linkButton: {padding:'8px 12px',backgroundColor:'#ff8c00',color:'#fff',border:'none',borderRadius:'5px',cursor:'pointer'}
};

export default App;
