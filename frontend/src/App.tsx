import { useEffect, useRef, useState } from 'react'

declare global {
  interface Window {
    kakao: any
  }
}

interface Product {
  id: number
  martId: number
  name: string
  price: number
  eventType: string
}

function App() {
  const mapRef = useRef<HTMLDivElement>(null)
  const [products, setProducts] = useState<Product[]>([])

  // Spring Boot API 호출
  useEffect(() => {
    fetch('http://localhost:8081/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data)
        console.log('상품 데이터:', data)
      })
      .catch(err => console.error('API 호출 실패:', err))
  }, [])

  // 카카오맵 로딩
  useEffect(() => {
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false`
    script.async = true
    document.head.appendChild(script)

    script.onload = () => {
      window.kakao.maps.load(() => {
        if (!mapRef.current) return
        const options = {
          center: new window.kakao.maps.LatLng(37.5665, 126.9780),
          level: 3
        }
        new window.kakao.maps.Map(mapRef.current, options)
      })
    }
  }, [])

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* 지도 영역 */}
      <div ref={mapRef} style={{ flex: 1 }} />

      {/* 상품 리스트 영역 */}
      <div style={{ width: '300px', overflowY: 'auto', padding: '16px' }}>
        <h2>행사 상품 ({products.length}개)</h2>
        {products.map(product => (
          <div key={product.id} style={{ borderBottom: '1px solid #eee', padding: '8px 0' }}>
            <div style={{ fontWeight: 'bold' }}>{product.name}</div>
            <div>{product.price.toLocaleString()}원</div>
            <div style={{ color: 'red' }}>{product.eventType}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App